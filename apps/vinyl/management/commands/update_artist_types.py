from django.core.management.base import BaseCommand
from apps.vinyl.models import Artist

class Command(BaseCommand):
    help = 'Update artist types for existing artists'

    def handle(self, *args, **options):
        # Define artist types
        artist_types = {
            'male': ['Bob Dylan', 'Miles Davis', 'Stevie Wonder', 'David Bowie', 'Prince', 
                     'Michael Jackson', 'Elvis Presley', 'Johnny Cash', 'John Coltrane', 'Kendrick Lamar'],
            'female': ['Aretha Franklin', 'Madonna', 'Joni Mitchell', 'Billie Holiday', 
                       'Amy Winehouse', 'Beyoncé', 'Adele', 'Taylor Swift'],
            'band': ['The Beatles', 'Pink Floyd', 'Led Zeppelin', 'The Rolling Stones', 
                     'Queen', 'The Beach Boys', 'Radiohead', 'Nirvana']
        }

        # Update artist types
        updated_count = 0
        for artist_type, names in artist_types.items():
            for name in names:
                try:
                    artist = Artist.objects.get(name=name)
                    artist.artist_type = artist_type
                    artist.save()
                    self.stdout.write(f'Updated {name} to {artist_type}')
                    updated_count += 1
                except Artist.DoesNotExist:
                    self.stdout.write(f'Artist {name} not found')

        self.stdout.write(f'\nUpdated {updated_count} artists')
        
        # Show final count by type
        self.stdout.write("\nFinal count by type:")
        for artist_type in ['male', 'female', 'band', 'other']:
            count = Artist.objects.filter(artist_type=artist_type).count()
            self.stdout.write(f'{artist_type.title()}: {count} artists')
