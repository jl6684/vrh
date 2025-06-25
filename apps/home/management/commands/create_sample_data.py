from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.accounts.models import UserProfile
import random


class Command(BaseCommand):
    help = 'Create sample data for testing the vinyl shop'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating sample data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            VinylRecord.objects.all().delete()
            Artist.objects.all().delete()
            Genre.objects.all().delete()
            Label.objects.all().delete()
            # Keep users but remove their profiles for recreation
            UserProfile.objects.all().delete()
            self.stdout.write('Existing data cleared.')
        
        self.stdout.write('Creating sample data...')
        
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@vinylhouse.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            # Create admin profile
            UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'phone': '+1-555-0100',
                    'address': '123 Admin Street',
                    'city': 'New York',
                    'country': 'United States',
                    'postal_code': '10001',
                    'newsletter_subscription': True,
                    'email_notifications': True,
                }
            )
            self.stdout.write(f'Created admin user: admin/admin123')
        
        # Create sample regular user
        if not User.objects.filter(username='testuser').exists():
            test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            # Create test user profile
            UserProfile.objects.get_or_create(
                user=test_user,
                defaults={
                    'phone': '+1-555-0200',
                    'address': '456 Test Avenue',
                    'city': 'Los Angeles',
                    'country': 'United States',
                    'postal_code': '90210',
                    'newsletter_subscription': True,
                    'email_notifications': False,
                }
            )
            self.stdout.write(f'Created test user: testuser/testpass123')
        
        # Create genres
        genres_data = [
            'Rock', 'Pop', 'Jazz', 'Blues', 'Classical', 'Electronic',
            'Hip-Hop', 'R&B', 'Country', 'Folk', 'Reggae', 'Punk',
            'Alternative', 'Indie', 'Funk', 'Soul'
        ]
        
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
        labels_data = [
            'Atlantic Records', 'Columbia Records', 'EMI', 'Universal Music',
            'Warner Bros. Records', 'Capitol Records', 'Sony Music', 'RCA Records',
            'Motown Records', 'Blue Note Records', 'Verve Records', 'Def Jam'
        ]
        
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
        artists_data = [
            # Male Artists
            {'name': 'Bob Dylan', 'type': 'male', 'country': 'United States'},
            {'name': 'Miles Davis', 'type': 'male', 'country': 'United States'},
            {'name': 'Stevie Wonder', 'type': 'male', 'country': 'United States'},
            {'name': 'David Bowie', 'type': 'male', 'country': 'United Kingdom'},
            {'name': 'Prince', 'type': 'male', 'country': 'United States'},
            {'name': 'Michael Jackson', 'type': 'male', 'country': 'United States'},
            {'name': 'Elvis Presley', 'type': 'male', 'country': 'United States'},
            {'name': 'Johnny Cash', 'type': 'male', 'country': 'United States'},
            {'name': 'John Coltrane', 'type': 'male', 'country': 'United States'},
            {'name': 'Kendrick Lamar', 'type': 'male', 'country': 'United States'},
            
            # Female Artists
            {'name': 'Aretha Franklin', 'type': 'female', 'country': 'United States'},
            {'name': 'Madonna', 'type': 'female', 'country': 'United States'},
            {'name': 'Joni Mitchell', 'type': 'female', 'country': 'Canada'},
            {'name': 'Billie Holiday', 'type': 'female', 'country': 'United States'},
            {'name': 'Amy Winehouse', 'type': 'female', 'country': 'United Kingdom'},
            {'name': 'Beyoncé', 'type': 'female', 'country': 'United States'},
            {'name': 'Adele', 'type': 'female', 'country': 'United Kingdom'},
            {'name': 'Taylor Swift', 'type': 'female', 'country': 'United States'},
            
            # Bands
            {'name': 'The Beatles', 'type': 'band', 'country': 'United Kingdom'},
            {'name': 'Pink Floyd', 'type': 'band', 'country': 'United Kingdom'},
            {'name': 'Led Zeppelin', 'type': 'band', 'country': 'United Kingdom'},
            {'name': 'The Rolling Stones', 'type': 'band', 'country': 'United Kingdom'},
            {'name': 'Queen', 'type': 'band', 'country': 'United Kingdom'},
            {'name': 'The Beach Boys', 'type': 'band', 'country': 'United States'},
            {'name': 'Radiohead', 'type': 'band', 'country': 'United Kingdom'},
            {'name': 'Nirvana', 'type': 'band', 'country': 'United States'},
        ]
        
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
        vinyl_records_data = [
            # Beatles
            {'title': 'Abbey Road', 'artist': 'The Beatles', 'genre': 'Rock', 'year': 1969, 'price': 30},
            {'title': 'Sgt. Pepper\'s Lonely Hearts Club Band', 'artist': 'The Beatles', 'genre': 'Rock', 'year': 1967, 'price': 35},
            {'title': 'Revolver', 'artist': 'The Beatles', 'genre': 'Rock', 'year': 1966, 'price': 32},
            
            # Bob Dylan
            {'title': 'Highway 61 Revisited', 'artist': 'Bob Dylan', 'genre': 'Folk', 'year': 1965, 'price': 28},
            {'title': 'Blood on the Tracks', 'artist': 'Bob Dylan', 'genre': 'Folk', 'year': 1975, 'price': 29},
            
            # Miles Davis
            {'title': 'Kind of Blue', 'artist': 'Miles Davis', 'genre': 'Jazz', 'year': 1959, 'price': 33},
            {'title': 'Bitches Brew', 'artist': 'Miles Davis', 'genre': 'Jazz', 'year': 1970, 'price': 36},
            
            # Pink Floyd
            {'title': 'The Dark Side of the Moon', 'artist': 'Pink Floyd', 'genre': 'Rock', 'year': 1973, 'price': 34},
            {'title': 'The Wall', 'artist': 'Pink Floyd', 'genre': 'Rock', 'year': 1979, 'price': 40},
            {'title': 'Wish You Were Here', 'artist': 'Pink Floyd', 'genre': 'Rock', 'year': 1975, 'price': 32},
            
            # Led Zeppelin
            {'title': 'Led Zeppelin IV', 'artist': 'Led Zeppelin', 'genre': 'Rock', 'year': 1971, 'price': 31},
            {'title': 'Physical Graffiti', 'artist': 'Led Zeppelin', 'genre': 'Rock', 'year': 1975, 'price': 43},
            
            # More diverse collection
            {'title': 'Songs in the Key of Life', 'artist': 'Stevie Wonder', 'genre': 'Soul', 'year': 1976, 'price': 38},
            {'title': 'I Never Loved a Man the Way I Love You', 'artist': 'Aretha Franklin', 'genre': 'Soul', 'year': 1967, 'price': 27},
            {'title': 'The Rise and Fall of Ziggy Stardust', 'artist': 'David Bowie', 'genre': 'Rock', 'year': 1972, 'price': 30},
            {'title': 'Purple Rain', 'artist': 'Prince', 'genre': 'Pop', 'year': 1984, 'price': 29},
            {'title': 'Like a Virgin', 'artist': 'Madonna', 'genre': 'Pop', 'year': 1984, 'price': 25},
            {'title': 'Thriller', 'artist': 'Michael Jackson', 'genre': 'Pop', 'year': 1982, 'price': 33},
            {'title': 'Blue', 'artist': 'Joni Mitchell', 'genre': 'Folk', 'year': 1971, 'price': 31},
            {'title': 'Let It Bleed', 'artist': 'The Rolling Stones', 'genre': 'Rock', 'year': 1969, 'price': 30},
            
            # Modern artists
            {'title': 'OK Computer', 'artist': 'Radiohead', 'genre': 'Alternative', 'year': 1997, 'price': 32},
            {'title': 'Nevermind', 'artist': 'Nirvana', 'genre': 'Alternative', 'year': 1991, 'price': 28},
            {'title': 'Back to Black', 'artist': 'Amy Winehouse', 'genre': 'Soul', 'year': 2006, 'price': 27},
            {'title': 'good kid, m.A.A.d city', 'artist': 'Kendrick Lamar', 'genre': 'Hip-Hop', 'year': 2012, 'price': 30},
            {'title': 'Lemonade', 'artist': 'Beyoncé', 'genre': 'R&B', 'year': 2016, 'price': 35},
            
            # Additional classics
            {'title': 'Pet Sounds', 'artist': 'The Beach Boys', 'genre': 'Pop', 'year': 1966, 'price': 34},
            {'title': 'A Night at the Opera', 'artist': 'Queen', 'genre': 'Rock', 'year': 1975, 'price': 33},
            {'title': 'Lady Soul', 'artist': 'Aretha Franklin', 'genre': 'Soul', 'year': 1968, 'price': 26},
            {'title': 'The Sun Sessions', 'artist': 'Elvis Presley', 'genre': 'Rock', 'year': 1976, 'price': 31},
            {'title': 'At Folsom Prison', 'artist': 'Johnny Cash', 'genre': 'Country', 'year': 1968, 'price': 29},
            {'title': 'A Love Supreme', 'artist': 'John Coltrane', 'genre': 'Jazz', 'year': 1965, 'price': 37},
            {'title': 'Lady in Satin', 'artist': 'Billie Holiday', 'genre': 'Jazz', 'year': 1958, 'price': 32},
            {'title': '21', 'artist': 'Adele', 'genre': 'Pop', 'year': 2011, 'price': 28},
            {'title': '1989', 'artist': 'Taylor Swift', 'genre': 'Pop', 'year': 2014, 'price': 30},
        ]
        
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
