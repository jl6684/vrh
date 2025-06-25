from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.accounts.models import UserProfile
from decimal import Decimal
import random, os, csv, pandas as pd, re, gspread
from oauth2client.service_account import ServiceAccountCredentials
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
    help = 'Create sample data for testing the vinyl shop'

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

    def handle(self, *args, **options):
        ex_file = options.get('ex_file')
        if ex_file is not None:
            # METHOD 3: Excel File Import
            excel_filename = ex_file or 'vinyldata-ex.xlsx'
            self.stdout.write(f'Creating sample data from Excel file: {excel_filename}...')
            excel_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
                'data-for-import', excel_filename
            )
            if not os.path.exists(excel_path):
                self.stdout.write(self.style.ERROR(f'Error: Excel file not found at {excel_path}'))
                self.stdout.write(f'Available files in data-for-import folder:')
                data_import_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
                    'data-for-import'
                )
                if os.path.exists(data_import_dir):
                    for file in os.listdir(data_import_dir):
                        if file.endswith('.xlsx'):
                            self.stdout.write(f'  - {file}')
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
            gs_file = options.get('gs_file')
            if gs_file:
                if gs_file not in VALID_WORKSHEETS:
                    self.stdout.write(self.style.ERROR(f"Please input worksheet name of '{gs_file}' you want to import."))
                    return
                sheet_id = DEFAULT_SHEET_ID
                worksheet_name = gs_file
                self.stdout.write(f'Creating sample data from Google Sheet: {sheet_id} (worksheet: {worksheet_name})...')
                
                try:
                    csv_rows = read_gsheet_data(sheet_id, worksheet_name)
                    # Use the new comprehensive validation and normalization
                    csv_rows = validate_and_normalize_data(csv_rows)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Google Sheet error: {e}'))
                    return
                self.stdout.write(f'Successfully loaded {len(csv_rows)} records from Google Sheet {sheet_id}')
            else:
                # METHOD 1: CSV File Import
                csv_filename = options['csv_file']
                self.stdout.write(f'Creating sample data from {csv_filename}...')
                csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 'data-for-import', csv_filename)
                if not os.path.exists(csv_path):
                    self.stdout.write(self.style.ERROR(f'Error: CSV file not found at {csv_path}'))
                    self.stdout.write(f'Available files in data-for-import folder:')
                    data_import_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 'data-for-import')
                    if os.path.exists(data_import_dir):
                        for file in os.listdir(data_import_dir):
                            if file.endswith('.csv'):
                                self.stdout.write(f'  - {file}')
                    return
                
                try:
                    csv_rows = read_csv_data(csv_path)
                    # Use the new comprehensive validation and normalization
                    csv_rows = validate_and_normalize_data(csv_rows)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'CSV validation error: {e}'))
                    return
                self.stdout.write(f'Successfully loaded {len(csv_rows)} records from {csv_filename}')

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
        
        artists = []
        for artist_name in artists_data:
            artist, created = Artist.objects.get_or_create(
                name=artist_name,
                defaults={
                    'biography': f'{artist_name} is a renowned musical artist known for their exceptional contributions to music.',
                    'country': 'United States'
                }
            )
            artists.append(artist)
            if created:
                self.stdout.write(f'Created artist: {artist_name}')
        
        for record_data in vinyl_records_data:
            # Find the artist and genre objects
            try:
                artist = Artist.objects.get(name=record_data['artist'])
                genre = Genre.objects.get(name=record_data['genre'])
                label = random.choice(labels)
                
                vinyl, created = VinylRecord.objects.get_or_create(
                    title=record_data['title'],
                    artist=artist,
                    defaults={
                        'genre': genre,
                        'label': label,
                        'price': Decimal(str(record_data['price'])),
                        'release_year': record_data['year'],
                        'stock_quantity': random.randint(5, 50),
                        'is_available': True,
                        'condition': 'new',
                        'speed': '33',
                        'size': '12',
                        'description': f"Classic album {record_data['title']} by {record_data['artist']} from {record_data['year']}.",
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'✅ Created: {record_data["title"]} by {record_data["artist"]}')
                else:
                    self.stdout.write(f'📀 Already exists: {record_data["title"]} by {record_data["artist"]}')
            
            except (Artist.DoesNotExist, Genre.DoesNotExist) as e:
                self.stdout.write(f'❌ Error creating {record_data["title"]}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Sample data creation completed!\n'
                f'📊 Summary:\n'
                f'- {Genre.objects.count()} genres\n'
                f'- {Label.objects.count()} labels\n'
                f'- {Artist.objects.count()} artists\n'
                f'- {VinylRecord.objects.count()} vinyl records (✨ {created_count} new)\n'
                f'\n🔑 Login credentials:\n'
                f'Admin: admin / admin123\n'
                f'User: testuser / testpass123'
            )
        )