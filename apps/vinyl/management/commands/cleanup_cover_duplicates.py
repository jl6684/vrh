import os
import re
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.vinyl.models import VinylRecord


class Command(BaseCommand):
    help = 'Clean up duplicate vinyl cover files and optimize storage'

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
            help='Run without making any file system changes'
        )
        parser.add_argument(
            '--update-db',
            action='store_true',
            help='Update database records to point to the retained files'
        )

    def handle(self, *args, **options):
        covers_dir = options['covers_dir']
        dry_run = options['dry_run']
        update_db = options['update_db']
        
        # Get absolute path to covers directory
        if not os.path.isabs(covers_dir):
            covers_dir = os.path.join(settings.BASE_DIR, covers_dir)
        
        if not os.path.exists(covers_dir):
            raise CommandError(f'Covers directory not found: {covers_dir}')
        
        self.stdout.write(f'Scanning covers in: {covers_dir}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Get all image files
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif'}
        image_files = []
        
        for filename in os.listdir(covers_dir):
            if os.path.splitext(filename.lower())[1] in valid_extensions:
                image_files.append(filename)
        
        self.stdout.write(f'Found {len(image_files)} image files')
        
        # Group files by their base name (without Django's random suffix)
        file_groups = defaultdict(list)
        
        for filename in image_files:
            # Extract the base name without random suffix
            # Django adds random suffixes like _xY1z2Ab to avoid name conflicts
            base_name = re.sub(r'_[a-zA-Z0-9]{7}(\.[^.]+)$', r'\1', filename)
            
            # Original filenames (without underscores) should be preserved
            if ' ' in filename:
                # This is likely an original file
                file_groups[base_name].insert(0, filename)
            else:
                file_groups[base_name].append(filename)
        
        # Statistics
        stats = {
            'groups': len(file_groups),
            'originals': 0,
            'duplicates': 0,
            'deleted': 0,
            'db_updated': 0,
        }
        
        # Process each group
        for base_name, files in file_groups.items():
            # Count number of files in this group
            if len(files) == 1:
                stats['originals'] += 1
                continue
                
            stats['duplicates'] += len(files) - 1
            
            # Keep the first file (original) and delete the rest
            keeper = files[0]
            duplicates = files[1:]
            
            self.stdout.write(f'\nFound duplicates for {base_name}:')
            self.stdout.write(f'  Keeping: {keeper}')
            
            for duplicate in duplicates:
                self.stdout.write(f'  Deleting: {duplicate}')
                
                if not dry_run:
                    duplicate_path = os.path.join(covers_dir, duplicate)
                    try:
                        os.remove(duplicate_path)
                        stats['deleted'] += 1
                    except OSError as e:
                        self.stdout.write(self.style.ERROR(f'    Error deleting file: {e}'))
            
            # Update database records if requested
            if update_db and not dry_run:
                # Find records using any of the duplicate filenames
                for duplicate in duplicates:
                    records = VinylRecord.objects.filter(cover_image__iendswith=duplicate)
                    for record in records:
                        old_name = record.cover_image.name
                        new_name = os.path.join('vinyl_covers', keeper)
                        
                        record.cover_image.name = new_name
                        record.save(update_fields=['cover_image'])
                        
                        self.stdout.write(f'  Updated record: {record.title}')
                        self.stdout.write(f'    From: {old_name}')
                        self.stdout.write(f'    To:   {new_name}')
                        stats['db_updated'] += 1
        
        # Print summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('CLEANUP SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total image files scanned: {len(image_files)}')
        self.stdout.write(f'Unique image groups: {stats["groups"]}')
        self.stdout.write(f'Single files (no duplicates): {stats["originals"]}')
        self.stdout.write(f'Duplicate files found: {stats["duplicates"]}')
        self.stdout.write(f'Files deleted: {stats["deleted"]}')
        self.stdout.write(f'Database records updated: {stats["db_updated"]}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no changes were made'))
            self.stdout.write('Run without --dry-run to actually clean up files')
            if update_db:
                self.stdout.write('Use --update-db to update database records too')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully cleaned up {stats["deleted"]} duplicate files!'))
