from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os
import glob


class Command(BaseCommand):
    help = 'Update cover_image field in vinyl_vinylrecord table based on title field'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )
        parser.add_argument(
            '--file-extensions',
            type=str,
            default='.jpg,.jpeg,.png,.gif,.webp,.avif',
            help='Comma-separated list of file extensions to check (default: .jpg,.jpeg,.png,.gif,.webp,.avif)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        file_extensions = [ext.strip() for ext in options['file_extensions'].split(',')]
        
        # Ensure all file extensions start with a dot
        file_extensions = [ext if ext.startswith('.') else '.' + ext for ext in file_extensions]
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting vinyl cover image path update...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        self.stdout.write(f'Checking for file extensions: {", ".join(file_extensions)}')
        
        # Get the media root path from settings
        media_root = settings.MEDIA_ROOT
        vinyl_covers_path = os.path.join(media_root, 'vinyl_covers')
        
        self.stdout.write(f'Media root: {media_root}')
        self.stdout.write(f'Vinyl covers path: {vinyl_covers_path}')
        
        # Check if vinyl_covers directory exists
        if not os.path.exists(vinyl_covers_path):
            self.stdout.write(
                self.style.ERROR(f'Vinyl covers directory does not exist: {vinyl_covers_path}')
            )
            return
        
        with connection.cursor() as cursor:
            # Get all vinyl records with their current cover_image values
            cursor.execute("""
                SELECT id, title, cover_image 
                FROM vinyl_vinylrecord 
                ORDER BY id
            """)
            
            records = cursor.fetchall()
            
            if not records:
                self.stdout.write(
                    self.style.WARNING('No vinyl records found in database')
                )
                return
            
            self.stdout.write(f'Found {len(records)} vinyl records to process')
            
            updated_count = 0
            skipped_count = 0
            not_found_count = 0
            
            for record_id, title, current_cover_image in records:
                # Try to find the file with any of the supported extensions
                found_file = None
                found_extension = None
                
                for ext in file_extensions:
                    expected_path = f'vinyl_covers/{title}{ext}'
                    full_file_path = os.path.join(media_root, expected_path)
                    
                    if os.path.exists(full_file_path):
                        found_file = expected_path
                        found_extension = ext
                        break
                
                if found_file:
                    if current_cover_image == found_file:
                        self.stdout.write(
                            f'Record {record_id}: "{title}" - Path already correct ({found_file})'
                        )
                        skipped_count += 1
                    else:
                        if not dry_run:
                            # Update the cover_image field
                            cursor.execute("""
                                UPDATE vinyl_vinylrecord 
                                SET cover_image = %s 
                                WHERE id = %s
                            """, [found_file, record_id])
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Record {record_id}: "{title}" - Updated to {found_file}'
                                )
                            )
                        else:
                            self.stdout.write(
                                f'Record {record_id}: "{title}" - Would update to {found_file}'
                            )
                        updated_count += 1
                else:
                    # File not found with any extension
                    self.stdout.write(
                        self.style.WARNING(
                            f'Record {record_id}: "{title}" - No matching file found with extensions: {", ".join(file_extensions)}'
                        )
                    )
                    not_found_count += 1
            
            if not dry_run:
                connection.commit()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nUpdate completed! Updated: {updated_count}, Skipped: {skipped_count}, Not found: {not_found_count}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nDry run completed! Would update: {updated_count}, Would skip: {skipped_count}, Not found: {not_found_count}'
                    )
                ) 