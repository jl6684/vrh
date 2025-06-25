from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.accounts.models import UserProfile
from decimal import Decimal
import random
import os
import csv
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def read_csv_data_pandas(csv_path):
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


def extract_genres_data2(csv_rows):
    """Extract unique genres from CSV rows."""
    return list({row['genre'].strip() for row in csv_rows if row.get('genre')})


def extract_labels_data2(csv_rows):
    """Extract unique labels from CSV rows."""
    return list({row['label'].strip() for row in csv_rows if row.get('label')})


def extract_artists_data2(csv_rows):
    """Extract artist info as list of dicts from CSV rows."""
    seen = set()
    artists = []
    for row in csv_rows:
        key = (row['artist'].strip(), row['type'].strip(), row['country'].strip())
        if key not in seen:
            artists.append({
                'name': row['artist'].strip(),
                'type': row['type'].strip(),
                'country': row['country'].strip(),
            })
            seen.add(key)
    return artists


def extract_vinyl_records_data2(csv_rows):
    """Extract vinyl record info as list of dicts from CSV rows."""
    records = []
    for row in csv_rows:
        records.append({
            'title': row['title'].strip(),
            'artist': row['artist'].strip(),
            'genre': row['genre'].strip(),
            'year': int(row['year']),
            'price': int(row['price']),
        })
    return records


def read_excel_data(excel_path):
    """Read the Excel file and return a list of rows as dictionaries."""
    df = pd.read_excel(excel_path)
    return df.to_dict(orient='records')

# Example usage for Google Sheets (requires credentials.json and sharing the sheet with the service account email):
def read_gsheet_data(sheet_id, worksheet_name='Sheet1'):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id)
    worksheet = sheet.worksheet(worksheet_name)
    rows = worksheet.get_all_records()
    return rows


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
            sheet_id = gs_file if gs_file != 'vinyldata-gs.xlsx' else 'vinyldata-gs.xlsx'
            worksheet_name = 'Sheet1'  # You can make this configurable if needed
            self.stdout.write(f'Creating sample data from Google Sheet: {sheet_id} (worksheet: {worksheet_name})...')
            csv_rows = read_gsheet_data(sheet_id, worksheet_name)
            # Validate structure (same as CSV)
            try:
                validate_csv_structure(csv_rows)
            except Exception as e:
                self.stdout.write(f'Google Sheet validation error: {e}')
                return
            self.stdout.write(f'Successfully loaded {len(csv_rows)} records from Google Sheet {sheet_id}')
        else:
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
            csv_rows = read_csv_data_pandas(csv_path)
            try:
                validate_csv_structure(csv_rows)
            except Exception as e:
                self.stdout.write(f'CSV validation error: {e}')
                return
            self.stdout.write(f'Successfully loaded {len(csv_rows)} records from {csv_filename}')

        # genres_data = [
        #     'Rock', 'Pop', 'Jazz', 'Blues', 'Classical', 'Electronic',
        #     'Hip-Hop', 'R&B', 'Country', 'Folk', 'Reggae', 'Punk',
        #     'Alternative', 'Indie', 'Funk', 'Soul','Soundtrack'
        # ]
        genres_data = extract_genres_data2(csv_rows)

        # labels_data = [
        #     'Atlantic Records', 'Columbia Records', 'EMI', 'Universal Music',
        #     'Warner Bros. Records', 'Capitol Records', 'Sony Music', 'RCA Records',
        #     'Motown Records', 'Blue Note Records', 'Verve Records', 'Def Jam',
        #     'Polydor', '風行唱片', 'Deutsche Grammophon'
        # ]
        labels_data = extract_labels_data2(csv_rows)

        # artists_data = [
        #     ...
        # ]
        artists_data = extract_artists_data2(csv_rows)

        # vinyl_records_data = [
        #     ...
        # ]
        vinyl_records_data = extract_vinyl_records_data2(csv_rows)
        
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
        # labels_data = [
        #     'Atlantic Records', 'Columbia Records', 'EMI', 'Universal Music',
        #     'Warner Bros. Records', 'Capitol Records', 'Sony Music', 'RCA Records',
        #     'Motown Records', 'Blue Note Records', 'Verve Records', 'Def Jam',
        #     'Polydor', '風行唱片', 'Deutsche Grammophon'
        # ]
        
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
        
        # Create artists with types
        # artists_data = [
        #     # Male Artists
        #     {'name': 'Bob Dylan', 'type': 'male', 'country': 'United States'},
        #     {'name': 'Miles Davis', 'type': 'male', 'country': 'United States'},
        #     {'name': 'Stevie Wonder', 'type': 'male', 'country': 'United States'},
        #     {'name': 'David Bowie', 'type': 'male', 'country': 'United Kingdom'},
        #     {'name': 'Prince', 'type': 'male', 'country': 'United States'},
        #     {'name': 'Michael Jackson', 'type': 'male', 'country': 'United States'},
        #     {'name': 'Elvis Presley', 'type': 'male', 'country': 'United States'},
        #     {'name': 'Johnny Cash', 'type': 'male', 'country': 'United States'},
        #     {'name': 'John Coltrane', 'type': 'male', 'country': 'United States'},
        #     {'name': 'Kendrick Lamar', 'type': 'male', 'country': 'United States'},
        #     {'name': '許冠傑', 'type': 'male', 'country': 'Hong Kong'}, 
        #     {'name': '譚詠麟', 'type': 'male', 'country': 'Hong Kong'},
        #     {'name': '張國榮', 'type': 'male', 'country': 'Hong Kong'},
        #     {'name': '呂文成', 'type': 'male', 'country': 'China'},
        #     {'name': '陳百強', 'type': 'male', 'country': 'Hong Kong'},
            
        #     # Female Artists
        #     {'name': 'Aretha Franklin', 'type': 'female', 'country': 'United States'},
        #     {'name': 'Madonna', 'type': 'female', 'country': 'United States'},
        #     {'name': 'Joni Mitchell', 'type': 'female', 'country': 'Canada'},
        #     {'name': 'Billie Holiday', 'type': 'female', 'country': 'United States'},
        #     {'name': 'Amy Winehouse', 'type': 'female', 'country': 'United Kingdom'},
        #     {'name': 'Beyoncé', 'type': 'female', 'country': 'United States'},
        #     {'name': 'Adele', 'type': 'female', 'country': 'United Kingdom'},
        #     {'name': 'Taylor Swift', 'type': 'female', 'country': 'United States'},
        #     {'name': '鄧麗君', 'type': 'female', 'country': 'Taiwan'},
        #     {'name': '梅艷芳', 'type': 'female', 'country': 'China'},
        #     {'name': '徐小鳳', 'type': 'female', 'country': 'China'},
        #     {'name': '蘇芮',   'type': 'female', 'country': 'China'},
        #     {'name': '葉蒨文', 'type': 'female', 'country': 'China'},
        #     {'name': '鳳飛飛', 'type': 'female', 'country': 'Taiwan'},
            
        #     # Bands
        #     {'name': 'The Beatles', 'type': 'band', 'country': 'United Kingdom'},
        #     {'name': 'Pink Floyd', 'type': 'band', 'country': 'United Kingdom'},
        #     {'name': 'Led Zeppelin', 'type': 'band', 'country': 'United Kingdom'},
        #     {'name': 'The Rolling Stones', 'type': 'band', 'country': 'United Kingdom'},
        #     {'name': 'Queen', 'type': 'band', 'country': 'United Kingdom'},
        #     {'name': 'The Beach Boys', 'type': 'band', 'country': 'United States'},
        #     {'name': 'Radiohead', 'type': 'band', 'country': 'United Kingdom'},
        #     {'name': 'Nirvana', 'type': 'band', 'country': 'United States'},
        #     {'name': '合眾中西樂團', 'type': 'band', 'country': 'Taiwan'},
        #     {'name': '風行國樂隊', 'type': 'band', 'country': 'Hong Kong'},
        #     {'name': '民間舞曲', 'type': 'band', 'country': 'China'},
        #     {'name': '鼓霸大樂隊', 'type': 'band', 'country': 'Taiwan'},
        #     {'name': 'Banzaii', 'type': 'band', 'country': 'Hong Kong'},

        #     # Assortments   
        #     {'name': 'Sakura FM-1403', 'type': 'Assortment', 'country': 'Japan'},
        #     {'name': 'Vintage B&W Records Cantonese Pop Promo', 'type': 'Assortment', 'country': 'Hong Kong'},
        #     {'name': 'Chinese Pathe Collection', 'type': 'Assortment', 'country': 'China'},
        #     {'name': 'Golden Era of Singaporean Pop', 'type': 'Assortment', 'country': 'Singapore'},
        #     {'name': 'Cantonese Drama Soundtracks', 'type': 'Assortment', 'country': 'Hong Kong'},
        #     {'name': 'Malaysian Chinese Promo Jukebox', 'type': 'Assortment', 'country': 'Malaysia'},

        #     # Classical       
        #     {'name': 'Herbert von Karajan & Berlin Philharmonic', 'type': 'Classical', 'country': 'Austria'},
        #     {'name': 'Columbia Symphony Orchestra / Igor Stravinsky', 'type': 'Classical', 'country': 'USA'},
        #     {'name': 'Sviatoslav Richter', 'type': 'Classical', 'country': 'Soviet Union'},
        #     {'name': 'Salvatore Accardo, Gewandhausorchester Leipzig, Kurt Masur', 'type': 'Classical', 'country': 'Italy'},
        #     {'name': 'Herbert von Karajan, Berlin Philharmonic', 'type': 'Classical', 'country': 'Austria'},
        #     {'name': 'Various Orchestras & Conductors', 'type': 'Classical', 'country': 'International'},
        # ]
        
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
        # vinyl_records_data = [
        #     # Beatles
        #     {'title': 'Abbey Road', 'artist': 'The Beatles', 'genre': 'Rock', 'year': 1969, 'price': 30},
        #     {'title': 'Sgt. Pepper\'s Lonely Hearts Club Band', 'artist': 'The Beatles', 'genre': 'Rock', 'year': 1967, 'price': 35},
        #     {'title': 'Revolver', 'artist': 'The Beatles', 'genre': 'Rock', 'year': 1966, 'price': 32},
            
        #     # Bob Dylan
        #     {'title': 'Highway 61 Revisited', 'artist': 'Bob Dylan', 'genre': 'Folk', 'year': 1965, 'price': 28},
        #     {'title': 'Blood on the Tracks', 'artist': 'Bob Dylan', 'genre': 'Folk', 'year': 1975, 'price': 29},
            
        #     # Miles Davis
        #     {'title': 'Kind of Blue', 'artist': 'Miles Davis', 'genre': 'Jazz', 'year': 1959, 'price': 33},
        #     {'title': 'Bitches Brew', 'artist': 'Miles Davis', 'genre': 'Jazz', 'year': 1970, 'price': 36},
            
        #     # Pink Floyd
        #     {'title': 'The Dark Side of the Moon', 'artist': 'Pink Floyd', 'genre': 'Rock', 'year': 1973, 'price': 34},
        #     {'title': 'The Wall', 'artist': 'Pink Floyd', 'genre': 'Rock', 'year': 1979, 'price': 40},
        #     {'title': 'Wish You Were Here', 'artist': 'Pink Floyd', 'genre': 'Rock', 'year': 1975, 'price': 32},
            
        #     # Led Zeppelin
        #     {'title': 'Led Zeppelin IV', 'artist': 'Led Zeppelin', 'genre': 'Rock', 'year': 1971, 'price': 31},
        #     {'title': 'Physical Graffiti', 'artist': 'Led Zeppelin', 'genre': 'Rock', 'year': 1975, 'price': 43},
            
        #     # More diverse collection
        #     {'title': 'Songs in the Key of Life', 'artist': 'Stevie Wonder', 'genre': 'Soul', 'year': 1976, 'price': 38},
        #     {'title': 'I Never Loved a Man the Way I Love You', 'artist': 'Aretha Franklin', 'genre': 'Soul', 'year': 1967, 'price': 27},
        #     {'title': 'The Rise and Fall of Ziggy Stardust', 'artist': 'David Bowie', 'genre': 'Rock', 'year': 1972, 'price': 30},
        #     {'title': 'Purple Rain', 'artist': 'Prince', 'genre': 'Pop', 'year': 1984, 'price': 29},
        #     {'title': 'Like a Virgin', 'artist': 'Madonna', 'genre': 'Pop', 'year': 1984, 'price': 25},
        #     {'title': 'Thriller', 'artist': 'Michael Jackson', 'genre': 'Pop', 'year': 1982, 'price': 33},
        #     {'title': 'Blue', 'artist': 'Joni Mitchell', 'genre': 'Folk', 'year': 1971, 'price': 31},
        #     {'title': 'Let It Bleed', 'artist': 'The Rolling Stones', 'genre': 'Rock', 'year': 1969, 'price': 30},
            
        #     # Modern artists
        #     {'title': 'OK Computer', 'artist': 'Radiohead', 'genre': 'Alternative', 'year': 1997, 'price': 32},
        #     {'title': 'Nevermind', 'artist': 'Nirvana', 'genre': 'Alternative', 'year': 1991, 'price': 28},
        #     {'title': 'Back to Black', 'artist': 'Amy Winehouse', 'genre': 'Soul', 'year': 2006, 'price': 27},
        #     {'title': 'good kid, m.A.A.d city', 'artist': 'Kendrick Lamar', 'genre': 'Hip-Hop', 'year': 2012, 'price': 30},
        #     {'title': 'Lemonade', 'artist': 'Beyoncé', 'genre': 'R&B', 'year': 2016, 'price': 35},

        #     #Chinese collections
        #     {'title': '鬼馬雙星', 'artist': '許冠傑', 'genre': 'Pop', 'year': 1974, 'price': 420},
        #     {'title': '半斤八兩', 'artist': '許冠傑', 'genre': 'Pop', 'year': 1976, 'price': 400},
        #     {'title': '愛人女神', 'artist': '譚詠麟', 'genre': 'Pop', 'year': 1982, 'price': 600},
        #     {'title': '風繼續吹', 'artist': '張國榮', 'genre': 'Pop', 'year': 1983, 'price': 720},
        #     {'title': '中國傑作集', 'artist': '呂文成', 'genre': 'Folk', 'year': 1967, 'price': 430},
        #     {'title': '眼淚為你流', 'artist': '陳百強', 'genre': 'Pop', 'year': 1979, 'price': 500},
        #     {'title': '再見我的愛人', 'artist': '鄧麗君', 'genre': 'Pop', 'year': 1975, 'price': 2480},
        #     {'title': '壞女孩', 'artist': '梅艷芳', 'genre': 'Pop', 'year': 1985, 'price': 3200},
        #     {'title': '每一步', 'artist': '徐小鳳', 'genre': 'Pop', 'year': 1986, 'price': 1950},
        #     {'title': '搭錯車電影原聲帶', 'artist': '蘇芮', 'genre': 'Soundtrack', 'year': 1983, 'price': 2850},
        #     {'title': '祝福', 'artist': '葉蒨文', 'genre': 'Pop', 'year': 1988, 'price': 1780},
        #     {'title': '我是一片雲', 'artist': '鳳飛飛', 'genre': 'Folk', 'year': 1977, 'price': 2100},
        #     {'title': '雙鳳朝陽', 'artist': '合衆中西樂團', 'genre': 'Folk', 'year': 1967, 'price': 380},
        #     {'title': '新編廣東音樂 娛樂昇平', 'artist': '風行國樂隊', 'genre': 'Folk', 'year': 1960, 'price': 420},
        #     {'title': '金蛇狂舞', 'artist': '民間舞曲', 'genre': 'Folk', 'year': 1965, 'price': 300},
        #     {'title': '四喜臨門', 'artist': '風行國樂隊', 'genre': 'Folk', 'year': 1971, 'price': 460},
        #     {'title': '讓我慢慢告訴你', 'artist': '鼓霸大樂隊', 'genre': 'Jazz', 'year': 1970, 'price': 720},
        #     {'title': 'Chinese Kung Fu', 'artist': 'Banzaii', 'genre': 'Funk', 'year': 1975, 'price': 80},
        #     {'title': 'Sakura FM-1403', 'artist': 'Assortment', 'genre': 'Pop', 'year': 1965, 'price': 480},
        #     {'title': 'Vintage B&W Records Cantonese Pop Promo', 'artist': 'Assortment', 'genre': 'Pop', 'year': 1987, 'price': 550},
        #     {'title': 'Chinese Pathe Collection', 'artist': 'Assortment', 'genre': 'Folk', 'year': 1967, 'price': 300},
        #     {'title': 'Golden Era of Singaporean Pop', 'artist': 'Assortment', 'genre': 'Pop', 'year': 1978, 'price': 400},
        #     {'title': 'Cantonese Drama Soundtracks', 'artist': 'Assortment', 'genre': 'Soundtrack', 'year': 1985, 'price': 620},
        #     {'title': 'Malaysian Chinese Promo Jukebox', 'artist': 'Assortment', 'genre': 'Pop', 'year': 1990, 'price': 180},

        #     # Classical
        #     {'title': 'Beethoven: IX. Symphonie', 'artist': 'Herbert von Karajan & Berlin Philharmonic', 'genre': 'Classical', 'year': 1963, 'price': 5070},
        #     {'title': 'Stravinsky Conducts Le Sacre du printemps', 'artist': 'Columbia Symphony Orchestra / Igor Stravinsky', 'genre': 'Classical', 'year': 1961, 'price': 3900},
        #     {'title': 'Chopin-Polonaises', 'artist': 'Sviatoslav Richter', 'genre': 'Classical', 'year': 1960, 'price': 430},
        #     {'title': 'Beethoven-Violin Concerto', 'artist': 'Salvatore Accardo, Gewandhausorchester Leipzig, Kurt Masur', 'genre': 'Classical', 'year': 1981, 'price': 117},
        #     {'title': 'Bruckner-The Symphonies', 'artist': 'Herbert von Karajan, Berlin Philharmonic', 'genre': 'Classical', 'year': 1976, 'price': 390},
        #     {'title': 'Beethoven Bicentennial Collection', 'artist': 'Various Orchestras & Conductors', 'genre': 'Classical', 'year': 1970, 'price': 1170},
        # ]
        
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
                f'\nLogin credentials:\n'
                f'Admin: admin / admin123\n'
                f'User: testuser / testpass123'
            )
        )
