import os, random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.accounts.models import UserProfile
from .data_import_helper import (
    normalize_field_delimiters,
    validate_normalized_data,
    validate_and_normalize_data,
    validate_csv_structure,
    validate_data_types,
    extract_genres_data,
    extract_labels_data,
    extract_artists_data,
    extract_vinyl_records_data,
)
from .data_import_method import (
    read_csv_data,
    read_gsheet_data,
    read_excel_data,
    DEFAULT_SHEET_ID,
    VALID_WORKSHEETS,
)

# Introduced a DATA_IMPORT_DIR constant for the data-for-import path, used throughout the script.
DATA_IMPORT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    'data-for-import'
)

# Added a helper function to list files by extension, used in print_available_files.
def list_files_by_extension(directory, extension):
    if os.path.exists(directory):
        return [file for file in os.listdir(directory) if file.endswith(extension)]
    return []

# ============================================================================
# DJANGO MANAGEMENT COMMAND: DATA IMPORT ENTRY POINT
# The Command(BaseCommand) class below defines the CLI interface for importing
# sample data into the system. It uses add_arguments to define CLI options
# and the handle() method to coordinate the import process using the shared
# and method-specific helper functions.
# Supported import methods:
#   --csv-file: Import from CSV
#   --gs-file:  Import from Google Sheets
#   --ex-file:  Import from Excel
# ============================================================================

class Command(BaseCommand):
    help = 'Import data for Vinyl Record Home business website.'

    # Added a helper function to print available files by extension, used in print_available_files.
    def print_available_files(self, directory, extension):
        self.stdout.write(f'Available files in data-for-import folder:')
        for file in list_files_by_extension(directory, extension):
            self.stdout.write(f'  - {file}')

    # Added a method to add arguments to the command, used in the handle() method.
    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='vinyldata.csv',
            help='Name of the CSV file in data-for-import folder (default: vinyldata.csv)'
        )
        parser.add_argument(
            '--gs-file',
            type=str,
            nargs='?',
            const='vinyldata-gs.xlsx',
            default=None,
            help='Google Sheet ID to import data from. If not provided, defaults to vinyldata-gs.xlsx.'
        )
        parser.add_argument(
            '--ex-file',
            type=str,
            nargs='?',
            const='vinyldata-ex.xlsx',
            default=None,
            help='Name of the Excel file in data-for-import folder (default: vinyldata-ex.xlsx)'
        )

    # Added a method to handle the command, used in the handle() method.
    def handle(self, *args, **options):
        ex_file = options.get('ex_file')
        if ex_file is not None:
            # METHOD 3: Excel File Import
            excel_filename = ex_file or 'vinyldata-ex.xlsx'
            self.stdout.write(f'Creating sample data from Excel file: {excel_filename}...')
            excel_path = os.path.join(DATA_IMPORT_DIR, excel_filename)
            if not os.path.exists(excel_path):
                self.stdout.write(self.style.ERROR(f'Error: Excel file not found at {excel_path}'))
                self.print_available_files(DATA_IMPORT_DIR, '.xlsx')
                return
            try:
                excel_rows = read_excel_data(excel_path)
                excel_rows = validate_and_normalize_data(excel_rows)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Excel validation error: {e}'))
                return
            self.stdout.write(f'Successfully loaded {len(excel_rows)} records from {excel_filename}')
            csv_rows = excel_rows  # For downstream processing
        else:
            # METHOD 2: Google Sheet Import
            gs_file = options.get('gs_file')
            if gs_file:
                if gs_file not in VALID_WORKSHEETS:
                    self.stdout.write(self.style.ERROR(f"Please input correct worksheet name to import.(Case sensitive!!!)"))
                    return
                sheet_id = DEFAULT_SHEET_ID
                worksheet_name = gs_file
                self.stdout.write(f'Creating sample data from Google Sheet: {sheet_id} (worksheet: {worksheet_name})...')
                try:
                    csv_rows = read_gsheet_data(sheet_id, worksheet_name)
                    csv_rows = validate_and_normalize_data(csv_rows)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Google Sheet error: {e}'))
                    return
                self.stdout.write(f'Successfully loaded {len(csv_rows)} records from Google Sheet {sheet_id}')
            else:
                # METHOD 1: CSV File Import
                csv_filename = options['csv_file']
                self.stdout.write(f'Creating sample data from {csv_filename}...')
                csv_path = os.path.join(DATA_IMPORT_DIR, csv_filename)
                if not os.path.exists(csv_path):
                    self.stdout.write(self.style.ERROR(f'Error: CSV file not found at {csv_path}'))
                    self.print_available_files(DATA_IMPORT_DIR, '.csv')
                    return
                try:
                    csv_rows = read_csv_data(csv_path)
                    csv_rows = validate_and_normalize_data(csv_rows)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'CSV validation error: {e}'))
                    return
                self.stdout.write(f'Successfully loaded {len(csv_rows)} records from {csv_filename}')

        # Extract data from the CSV rows
        genres_data = extract_genres_data(csv_rows)
        labels_data = extract_labels_data(csv_rows)
        artists_data = extract_artists_data(csv_rows)
        vinyl_records_data = extract_vinyl_records_data(csv_rows)
        
        # Create genres
        genres = []
        for genre_name in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=genre_name,
                defaults={'name': genre_name}
            )
            genres.append(genre)
            if created:
                self.stdout.write(f'Created genre: {genre_name}')
        
        # Create labels
        labels = []
        for label_name in labels_data:
            label, created = Label.objects.get_or_create(
                name=label_name,
                defaults={
                    'country': 'United States',
                    'website': f'https://www.{label_name.lower().replace(" ", "").replace(".", "")}.com'
                }
            )
            labels.append(label)
            if created:
                self.stdout.write(f'Created label: {label_name}')
        
        # Create artists
        artists = []
        for artist_data in artists_data:
            artist, created = Artist.objects.get_or_create(
                name=artist_data['name'],
                defaults={
                    'artist_type': artist_data['type'],
                    'biography': f'{artist_data["name"]} is a renowned musical artist known for their exceptional contributions to music.',
                    'country': artist_data['country']
                }
            )
            # Update existing artists with type if they don't have one
            if not created and not artist.artist_type:
                artist.artist_type = artist_data['type']
                artist.save()
                self.stdout.write(f'Updated artist type for: {artist_data["name"]}')
            artists.append(artist)
            if created:
                self.stdout.write(f'Created artist: {artist_data["name"]} ({artist_data["type"]})')
        
        # Create vinyl records
        for record_data in vinyl_records_data:
            # Find the artist and genre objects
            try:
                artist = Artist.objects.get(name=record_data['artist'])
                genre = Genre.objects.get(name=record_data['genre'])
                label = random.choice(labels)
                
                # Add some variety to conditions and physical properties
                conditions = ['new', 'mint', 'very_good', 'good']
                sizes = ['12', '12', '12', '7']  # Mostly 12" with some 7"
                speeds = ['33', '33', '45'] if random.choice(sizes) == '7' else ['33']
                vinyl, created = VinylRecord.objects.get_or_create(
                    title=record_data['title'],
                    artist=artist,
                    defaults={
                        'genre': genre,
                        'label': label,
                        'price': record_data['price'],
                        'release_year': record_data['year'],
                        'stock_quantity': random.randint(5, 50),
                        'is_available': True,
                        'condition': random.choice(conditions),
                        'speed': random.choice(speeds),
                        'size': random.choice(sizes),
                        'description': f"Classic album {record_data['title']} by {record_data['artist']} from {record_data['year']}. A must-have for any vinyl collection.",
                        'featured': random.choice([True, False]) if random.random() < 0.3 else False,
                        'weight': round(random.uniform(120, 180), 2),  # Typical vinyl weight in grams
                    }
                )
                                
                if created:
                    self.stdout.write(f'Created vinyl: {record_data["title"]} by {record_data["artist"]}')
            except (Artist.DoesNotExist, Genre.DoesNotExist) as e:
                self.stdout.write(f'Error creating {record_data["title"]}: {e}')
        
        # Print summary of created data
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample data created successfully!\n'
                f'- {Genre.objects.count()} genres\n'
                f'- {Label.objects.count()} labels\n'
                f'- {Artist.objects.count()} artists\n'
                f'- {VinylRecord.objects.count()} vinyl records\n'
                f'- {User.objects.count()} users\n'
                f'- {UserProfile.objects.count()} user profiles\n'
                f'\nLogin credentials:\n'
                f'Admin: admin / admin123\n'
                f'User: testuser / testpass123\n'
                f'\nTo clear and recreate data, use: python manage.py import_vinyl_data --clear'
            )
        )