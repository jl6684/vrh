from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.accounts.models import UserProfile
from decimal import Decimal
import random, os, csv, pandas as pd, re, gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============================================================================
# METHOD 1: CSV FILE IMPORT FUNCTIONS
# ============================================================================

def read_csv_data(csv_path):
    """Read CSV using pandas with better error handling."""
    try:
        df = pd.read_csv(csv_path, encoding='utf-8')
        return df.to_dict(orient='records')
    except pd.errors.ParserError as e:
        # Try with different parsing options
        try:
            df = pd.read_csv(csv_path, encoding='utf-8', quoting=csv.QUOTE_ALL)
            return df.to_dict(orient='records')
        except pd.errors.ParserError:
            # If still failing, provide detailed error information
            raise Exception(f"CSV parsing error in {csv_path}. Please check:\n"
                f"1. All fields with commas are properly quoted\n"
                f"2. Each row has exactly 8 columns\n"
                f"3. No extra commas in data fields\n"
                f"Original error: {str(e)}")


def validate_csv_structure(csv_rows):
    """Validate that CSV has the expected structure and provide helpful error messages."""
    expected_columns = ['title', 'artist', 'genre', 'year', 'price', 'type', 'country', 'label']
    
    if not csv_rows:
        raise Exception("CSV file is empty or could not be parsed")
    
    # Check if all expected columns are present
    first_row = csv_rows[0]
    missing_columns = [col for col in expected_columns if col not in first_row]
    if missing_columns:
        raise Exception(f"Missing required columns: {missing_columns}")
    
    # Check for rows with wrong number of fields
    for i, row in enumerate(csv_rows, start=2):  # start=2 because row 1 is header
        if len(row) != len(expected_columns):
            raise Exception(f"Row {i} has {len(row)} fields, expected {len(expected_columns)}. "
                f"Check for unquoted commas in: {row}")
    
    return True


def validate_data_types(csv_rows):
    """Validate that all required fields contain string data, not NaN/float."""
    for i, row in enumerate(csv_rows, start=2):  # start=2 because row 1 is header
        for field in ['title', 'artist', 'genre', 'type', 'country', 'label']:
            if pd.isna(row.get(field)) or not isinstance(row.get(field), str):
                raise Exception(f"Row {i}: Field '{field}' contains invalid data: {row.get(field)}. "
                    f"Expected string, got {type(row.get(field)).__name__}. "
                    f"This indicates commas appeared in data fields but unquoted. Please review the CSV file.")


def extract_genres_data(csv_rows):
    """Extract unique genres from CSV rows."""
    return list({str(row['genre']).strip() for row in csv_rows if row.get('genre') and pd.notna(row.get('genre'))})


def extract_labels_data(csv_rows):
    """Extract unique labels from CSV rows."""
    return list({str(row['label']).strip() for row in csv_rows if row.get('label') and pd.notna(row.get('label'))})


def extract_artists_data(csv_rows):
    """Extract artist info as list of dicts from CSV rows."""
    seen = set()
    artists = []
    for row in csv_rows:
        # Convert to string and handle NaN values
        artist_name = str(row['artist']).strip() if pd.notna(row.get('artist')) else ''
        artist_type = str(row['type']).strip() if pd.notna(row.get('type')) else ''
        artist_country = str(row['country']).strip() if pd.notna(row.get('country')) else ''
        
        if artist_name and artist_type and artist_country:
            key = (artist_name, artist_type, artist_country)
            if key not in seen:
                artists.append({
                    'name': artist_name,
                    'type': artist_type,
                    'country': artist_country,
                })
                seen.add(key)
    return artists


def extract_vinyl_records_data(csv_rows):
    """Extract vinyl record info as list of dicts from CSV rows."""
    records = []
    for row in csv_rows:
        # Convert to string and handle NaN values
        title = str(row['title']).strip() if pd.notna(row.get('title')) else ''
        artist = str(row['artist']).strip() if pd.notna(row.get('artist')) else ''
        genre = str(row['genre']).strip() if pd.notna(row.get('genre')) else ''
        
        # Handle numeric fields
        try:
            year = int(row['year']) if pd.notna(row.get('year')) else 0
            price = int(row['price']) if pd.notna(row.get('price')) else 0
        except (ValueError, TypeError):
            continue  # Skip rows with invalid numeric data
        
        if title and artist and genre and year > 0 and price > 0:
            records.append({
                'title': title,
                'artist': artist,
                'genre': genre,
                'year': year,
                'price': price,
            })
    return records


# ============================================================================
# METHOD 2: GOOGLE SHEETS IMPORT FUNCTIONS
# ============================================================================

DEFAULT_SHEET_ID = "1VmJAB5tM0mok7j5ma15qw8Ozshlp-kBnPKG5oa-D1rM"
VALID_WORKSHEETS = ["Sheet1", "Sheet2", "dupSheet2"]

def read_excel_data(excel_path):
    """Read Excel file with error handling."""
    try:
        df = pd.read_excel(excel_path)
        return df.to_dict(orient='records')
    except FileNotFoundError:
        raise Exception(f"Excel file not found: {excel_path}")
    except Exception as e:
        raise Exception(f"Error reading Excel file: {str(e)}")

def read_gsheet_data(sheet_id, worksheet_name='Sheet1'):
    """Read Google Sheet data with error handling."""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('gscredentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(worksheet_name)
        rows = worksheet.get_all_records()
        return rows
    except FileNotFoundError:
        raise Exception("gscredentials.json file not found. Please ensure Google Sheets credentials are properly configured.")
    except gspread.SpreadsheetNotFound:
        raise Exception(f"Google Sheet with ID '{sheet_id}' not found or not accessible.")
    except gspread.WorksheetNotFound:
        raise Exception(f"Worksheet '{worksheet_name}' not found in the Google Sheet.")
    except Exception as e:
        raise Exception(f"Error accessing Google Sheet: {str(e)}")


def normalize_field_delimiters(csv_rows):
    """
    Normalize delimiters in artist, genre, and label fields:
    - Replace ",", "|", "and" with "&"
    - Keep existing "&" unchanged
    - Ensure single space before and after "&"
    """
    normalized_rows = []
    for i, row in enumerate(csv_rows):
        normalized_row = row.copy()
        fields_to_normalize = ['artist', 'genre', 'label']
        for field in fields_to_normalize:
            if field in normalized_row and pd.notna(normalized_row[field]):
                value = str(normalized_row[field]).strip()
                if not value:
                    continue
                # Step 1: Replace all delimiters (comma, pipe, and "and") with " & "
                # Use regex to replace all at once, including cases with/without spaces
                value = re.sub(r'\s*(,|\||\\band\\b)\s*', ' & ', value, flags=re.IGNORECASE)
                # Step 2: Normalize spacing around "&"
                value = re.sub(r'\s*&\s*', ' & ', value)
                # Step 3: Clean up any remaining multiple spaces
                value = re.sub(r'\s+', ' ', value)
                # Step 4: Strip leading/trailing spaces
                value = value.strip()
                normalized_row[field] = value
        normalized_rows.append(normalized_row)
    return normalized_rows


def validate_normalized_data(csv_rows):
    """
    Validate that normalized data meets the formatting requirements.
    """
    for i, row in enumerate(csv_rows, start=2):
        for field in ['artist', 'genre', 'label']:
            if field in row and pd.notna(row[field]):
                value = str(row[field]).strip()
                
                # Check for proper "&" formatting
                if '&' in value:
                    # Should match: "A & B", "A & B & C", etc. (no leading/trailing &, single space around each &)
                    if not re.match(r'^[^&]+( & [^&]+)+$', value):
                        raise Exception(
                            f"Row {i}: Field '{field}' has improper spacing around '&': '{value}'. "
                            f"Expected format: 'Artist1 & Artist2 [ & Artist3 ...]'"
                        )
                
                # Check for remaining commas, pipes, or "and"
                if ',' in value or '|' in value or re.search(r'\band\b', value, re.IGNORECASE):
                    raise Exception(
                        f"Row {i}: Field '{field}' still contains unnormalized delimiters: '{value}'. "
                        f"Expected only '&' as delimiter."
                    )


def validate_and_normalize_data(csv_rows):
    """
    Comprehensive data validation and normalization:
    1. Validate structure and data types
    2. Normalize delimiters in artist, genre, and label fields
    3. Validate normalized data
    """
    # First, validate the original structure
    validate_csv_structure(csv_rows)
    validate_data_types(csv_rows)
    
    # Then normalize the delimiters
    normalized_rows = normalize_field_delimiters(csv_rows)
    
    # Validate the normalized data
    validate_normalized_data(normalized_rows)
    
    return normalized_rows

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

    def handle(self, *args, **options):
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
                f'\nTo clear and recreate data, use: python manage.py create_sample_data --clear'
            )
        )