import os
import re
from difflib import SequenceMatcher
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.files import File
from apps.vinyl.models import VinylRecord


class Command(BaseCommand):
    help = 'Match vinyl record covers from vinyl_covers directory to existing records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--covers-dir',
            type=str,
            default='media/vinyl_covers',
            help='Path to the covers directory (relative to project root)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any database changes'
        )
        parser.add_argument(
            '--min-similarity',
            type=float,
            default=0.8,
            help='Minimum similarity score for fuzzy matching (0.0 to 1.0)'
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update records that already have cover images'
        )

    def similarity(self, a, b):
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def clean_filename(self, filename):
        """Remove file extension and clean filename for comparison"""
        # Remove extension
        name = os.path.splitext(filename)[0]
        # Replace underscores with spaces
        name = name.replace('_', ' ')
        # Remove special characters that might cause issues
        name = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', name)
        return name.strip()

    def find_best_match(self, title, cover_files, min_similarity):
        """Find the best matching cover file for a given title"""
        best_match = None
        best_score = 0
        
        cleaned_title = self.clean_filename(title)
        
        for cover_file in cover_files:
            cleaned_cover = self.clean_filename(cover_file)
            
            # Try exact match first
            if cleaned_title.lower() == cleaned_cover.lower():
                return cover_file, 1.0
            
            # Try fuzzy matching
            score = self.similarity(cleaned_title, cleaned_cover)
            if score > best_score and score >= min_similarity:
                best_score = score
                best_match = cover_file
        
        return best_match, best_score if best_match else 0

    def handle(self, *args, **options):
        covers_dir = options['covers_dir']
        dry_run = options['dry_run']
        min_similarity = options['min_similarity']
        update_existing = options['update_existing']
        
        # Get absolute path to covers directory
        if not os.path.isabs(covers_dir):
            covers_dir = os.path.join(settings.BASE_DIR, covers_dir)
        
        if not os.path.exists(covers_dir):
            raise CommandError(f'Covers directory not found: {covers_dir}')
        
        self.stdout.write(f'Scanning covers in: {covers_dir}')
        self.stdout.write(f'Minimum similarity threshold: {min_similarity}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to the database'))
        
        # Get all cover files
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}
        cover_files = []
        
        for filename in os.listdir(covers_dir):
            if os.path.splitext(filename.lower())[1] in valid_extensions:
                cover_files.append(filename)
        
        self.stdout.write(f'Found {len(cover_files)} cover images')
        
        # Get vinyl records to process
        queryset = VinylRecord.objects.all()
        if not update_existing:
            queryset = queryset.filter(cover_image='')
        
        records = list(queryset)
        self.stdout.write(f'Found {len(records)} vinyl records to process')
        
        if not records:
            self.stdout.write(self.style.WARNING('No records to process'))
            return
        
        # Statistics
        stats = {
            'exact_matches': 0,
            'fuzzy_matches': 0,
            'no_matches': 0,
            'updated': 0,
            'skipped_existing': 0,
        }
        
        # Match covers to records
        matched_covers = set()
        
        for i, record in enumerate(records, 1):
            self.stdout.write(f'\nProcessing {i}/{len(records)}: "{record.title}"')
            
            # Skip if record already has cover and we're not updating
            if record.cover_image and not update_existing:
                self.stdout.write(f'  Skipping - already has cover: {record.cover_image.name}')
                stats['skipped_existing'] += 1
                continue
            
            # Find best matching cover
            best_match, score = self.find_best_match(record.title, cover_files, min_similarity)
            
            if best_match:
                if score == 1.0:
                    self.stdout.write(f'  ✓ Exact match: {best_match}')
                    stats['exact_matches'] += 1
                else:
                    self.stdout.write(f'  ≈ Fuzzy match ({score:.2f}): {best_match}')
                    stats['fuzzy_matches'] += 1
                
                # Check if this cover was already matched to another record
                if best_match in matched_covers:
                    self.stdout.write(f'    Warning: {best_match} already matched to another record')
                
                matched_covers.add(best_match)
                
                if not dry_run:
                    try:
                        # Create URL-safe filename
                        safe_filename = best_match.replace(' ', '_')
                        
                        # Check if the record already has this cover or a similarly named one
                        current_cover = os.path.basename(record.cover_image.name) if record.cover_image else None
                        
                        # Extract base filename without random suffix Django might have added
                        if current_cover:
                            # Remove random suffix like '_xY1z2Ab' that Django adds
                            base_current = re.sub(r'_[a-zA-Z0-9]{7}(\.[^.]+)$', r'\1', current_cover)
                            base_new = safe_filename
                            
                            # If already has the same cover (ignoring random suffix), skip
                            if base_current == base_new:
                                self.stdout.write(f'    Already has correct cover (as {current_cover}), skipping')
                                stats['updated'] += 1
                                continue
                        
                        # Get the path to the cover image, relative to MEDIA_ROOT
                        cover_path = os.path.join(covers_dir, best_match)
                        
                        # Calculate the relative path from MEDIA_ROOT
                        media_root = settings.MEDIA_ROOT
                        
                        # If the cover is already in MEDIA_ROOT, create a relative path
                        if cover_path.startswith(media_root):
                            relative_path = os.path.relpath(cover_path, media_root)
                        else:
                            # If it's outside MEDIA_ROOT, we need to create a symbolic link or copy it
                            self.stdout.write(self.style.WARNING(
                                f"Cover is outside MEDIA_ROOT. Using absolute path reference."
                            ))
                            relative_path = cover_path
                        
                        # Clear existing image reference if it exists
                        if record.cover_image:
                            # Just clear the reference, don't delete the actual file
                            record.cover_image = None
                        
                        # Directly set the name on the field without copying the file
                        record.cover_image.name = relative_path
                        record.save(update_fields=['cover_image'])
                        
                        self.stdout.write(f'    Updated database with cover: {safe_filename}')
                        stats['updated'] += 1
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'    Error updating record: {e}'))
                else:
                    self.stdout.write(f'    Would update with cover: {best_match}')
                    stats['updated'] += 1
            else:
                self.stdout.write(f'  ✗ No match found (best score: {score:.2f})')
                stats['no_matches'] += 1
        
        # Find unmatched covers
        unmatched_covers = set(cover_files) - matched_covers
        
        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('COVER MATCHING SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Records processed: {len(records)}')
        self.stdout.write(f'Exact matches: {stats["exact_matches"]}')
        self.stdout.write(f'Fuzzy matches: {stats["fuzzy_matches"]}')
        self.stdout.write(f'No matches: {stats["no_matches"]}')
        self.stdout.write(f'Records updated: {stats["updated"]}')
        self.stdout.write(f'Records skipped (already have covers): {stats["skipped_existing"]}')
        
        if unmatched_covers:
            self.stdout.write(f'\nUnmatched cover images ({len(unmatched_covers)}):')
            for cover in sorted(unmatched_covers):
                self.stdout.write(f'  - {cover}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no changes were made to the database'))
            self.stdout.write('Run without --dry-run to actually update the records')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated {stats["updated"]} vinyl records with cover images!'))
        
        # Suggestions for unmatched items
        if stats['no_matches'] > 0 or unmatched_covers:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('SUGGESTIONS FOR UNMATCHED ITEMS:')
            self.stdout.write('='*60)
            self.stdout.write('1. Check for typos in filenames or record titles')
            self.stdout.write('2. Lower the --min-similarity threshold (current: {})'.format(min_similarity))
            self.stdout.write('3. Manually rename cover files to match record titles exactly')
            self.stdout.write('4. Use Django admin to manually assign covers to specific records')
