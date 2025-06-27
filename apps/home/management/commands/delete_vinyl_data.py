"""
Django management command to delete vinyl data from the database.
Default action: Delete all records from vinyl_vinylrecord table only.
Optional: Delete specific tables using -artist, -genre, -label, or -all arguments.
"""
from django.core.management.base import BaseCommand
from apps.vinyl.models import VinylRecord, Artist, Genre, Label


class Command(BaseCommand):
    """Management command to delete vinyl-related data from database."""
    help = 'Delete vinyl data from database. Default: vinyl records only. Use -artist, -genre, -label, or -all for specific tables.'

    def add_arguments(self, parser):
        """Define command-line arguments for table-specific deletion and confirmation."""
        parser.add_argument(
            '-all',
            action='store_true',
            help='Delete all data in all 4 tables (vinyl records, artists, genres, labels)'
        )
        parser.add_argument(
            '-artist',
            action='store_true',
            help='Delete all data in vinyl_artist table'
        )
        parser.add_argument(
            '-genre',
            action='store_true',
            help='Delete all data in vinyl_genre table'
        )
        parser.add_argument(
            '-label',
            action='store_true',
            help='Delete all data in vinyl_label table'
        )
        parser.add_argument(
            '--force-delete',
            action='store_true',
            help='Delete without prompting for confirmation'
        )
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )


    def handle(self, *args, **options):
        """Main execution logic for deleting vinyl data."""
        delete_all = options.get('all', False)
        delete_artist = options.get('artist', False)
        delete_genre = options.get('genre', False)
        delete_label = options.get('label', False)
        force_delete = options.get('force_delete', False)
        test_only = options.get('test_only', False)

        # Determine what to delete based on arguments
        # Default: delete only vinyl records
        # If -all is specified, delete all 4 tables
        # If specific table arguments are provided, delete those + vinyl records
        if delete_all:
            tables_to_delete = {
                'vinyl_records': True,
                'artists': True,
                'genres': True,
                'labels': True
            }
        else:
            tables_to_delete = {
                'vinyl_records': True,  # Always delete vinyl records by default
                'artists': delete_artist,
                'genres': delete_genre,
                'labels': delete_label
            }

        # Get current record counts for tables that will be deleted
        vinyl_count = VinylRecord.objects.count() if tables_to_delete['vinyl_records'] else 0
        artist_count = Artist.objects.count() if tables_to_delete['artists'] else 0
        genre_count = Genre.objects.count() if tables_to_delete['genres'] else 0
        label_count = Label.objects.count() if tables_to_delete['labels'] else 0

        total_records = vinyl_count + artist_count + genre_count + label_count

        if total_records == 0:
            self.stdout.write(self.style.WARNING('No records found to delete.'))
            return

        if test_only:
            self.stdout.write(
                self.style.WARNING(
                    f'TEST ONLY - Would delete:\n'
                    f'- {vinyl_count} vinyl records\n'
                    f'- {artist_count} artists\n'
                    f'- {genre_count} genres\n'
                    f'- {label_count} labels\n'
                    f'Total: {total_records} records'
                )
            )
            return

        if not force_delete:
            self.stdout.write(
                self.style.WARNING(
                    f'About to delete:\n'
                    f'- {vinyl_count} vinyl records\n'
                    f'- {artist_count} artists\n'
                    f'- {genre_count} genres\n'
                    f'- {label_count} labels\n\n'
                    f'This action cannot be undone!'
                )
            )
            
            user_input = input('Are you sure you want to continue? (yes/no): ')
            if user_input.lower() not in ['yes', 'y']:
                self.stdout.write(self.style.ERROR('Deletion cancelled.'))
                return

        try:
            deleted_counts = {}
            
            # Delete vinyl records first (they reference other tables)
            if tables_to_delete['vinyl_records']:
                deleted_vinyl = VinylRecord.objects.all().delete()
                deleted_counts['vinyl'] = deleted_vinyl[0]
                self.stdout.write(f'Deleted {deleted_vinyl[0]} vinyl records')

            # Delete other tables if specified
            if tables_to_delete['artists']:
                deleted_artists = Artist.objects.all().delete()
                deleted_counts['artists'] = deleted_artists[0]
                self.stdout.write(f'Deleted {deleted_artists[0]} artists')

            if tables_to_delete['genres']:
                deleted_genres = Genre.objects.all().delete()
                deleted_counts['genres'] = deleted_genres[0]
                self.stdout.write(f'Deleted {deleted_genres[0]} genres')

            if tables_to_delete['labels']:
                deleted_labels = Label.objects.all().delete()
                deleted_counts['labels'] = deleted_labels[0]
                self.stdout.write(f'Deleted {deleted_labels[0]} labels')

            total_deleted = sum(deleted_counts.values())
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully deleted vinyl data!\n'
                    f'Total records deleted: {total_deleted}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error deleting data: {str(e)}')
            ) 