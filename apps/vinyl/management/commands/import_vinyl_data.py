import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.vinyl.models import VinylRecord, Artist, Genre, Label


class Command(BaseCommand):
    help = 'Import vinyl records from vinlydata.json file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data_exports/vinlydata.json',
            help='Path to the JSON file to import (relative to project root)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without making any database changes'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        dry_run = options['dry_run']
        
        # Get absolute path
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
        
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')
        
        self.stdout.write(f'Reading data from: {file_path}')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON file: {e}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made to the database'))
        
        self.stdout.write(f'Found {len(data)} records to process')
        
        # Statistics
        stats = {
            'artists_created': 0,
            'genres_created': 0,
            'labels_created': 0,
            'vinyl_records_created': 0,
            'vinyl_records_skipped': 0,
        }
        
        try:
            with transaction.atomic():
                for i, record in enumerate(data, 1):
                    self.stdout.write(f'Processing record {i}/{len(data)}: {record.get("title", "Unknown")}')
                    
                    # Create or get Genre
                    genre_obj = None
                    if record.get('genre'):
                        genre_obj, created = Genre.objects.get_or_create(
                            name=record['genre'],
                            defaults={'description': f'Genre: {record["genre"]}'}
                        )
                        if created and not dry_run:
                            stats['genres_created'] += 1
                            self.stdout.write(f'  Created genre: {genre_obj.name}')
                    
                    # Create or get Label
                    label_obj = None
                    if record.get('label') and record['label'] != 'Unknown':
                        label_obj, created = Label.objects.get_or_create(
                            name=record['label'],
                            defaults={'country': record.get('country', '')}
                        )
                        if created and not dry_run:
                            stats['labels_created'] += 1
                            self.stdout.write(f'  Created label: {label_obj.name}')
                    
                    # Create or get Artist
                    artist_obj = None
                    if record.get('artist'):
                        # Map the 'type' field to artist_type
                        artist_type_mapping = {
                            'male': 'male',
                            'female': 'female',
                            'band': 'band',
                            'Assortment': 'assortment',
                            'assortment': 'assortment',
                        }
                        artist_type = artist_type_mapping.get(record.get('type', ''), 'other')
                        
                        artist_obj, created = Artist.objects.get_or_create(
                            name=record['artist'],
                            defaults={
                                'artist_type': artist_type,
                                'country': record.get('country', ''),
                                'biography': f'Artist from {record.get("country", "Unknown location")}'
                            }
                        )
                        if created and not dry_run:
                            stats['artists_created'] += 1
                            self.stdout.write(f'  Created artist: {artist_obj.name} ({artist_type})')
                    
                    # Check if vinyl record already exists
                    if VinylRecord.objects.filter(
                        title=record.get('title', ''),
                        artist=artist_obj,
                        release_year=record.get('year', 0)
                    ).exists():
                        self.stdout.write(f'  Skipping duplicate: {record.get("title", "Unknown")}')
                        stats['vinyl_records_skipped'] += 1
                        continue
                    
                    # Create VinylRecord
                    if not dry_run:
                        vinyl_record = VinylRecord.objects.create(
                            title=record.get('title', 'Unknown Title'),
                            artist=artist_obj,
                            genre=genre_obj,
                            label=label_obj,
                            release_year=record.get('year', 1900),
                            price=record.get('price', 0),
                            stock_quantity=1,  # Default stock
                            is_available=True,
                            condition='new',  # Default condition
                            speed='33',  # Default speed
                            size='12',  # Default size
                        )
                        stats['vinyl_records_created'] += 1
                        self.stdout.write(f'  Created vinyl record: {vinyl_record.title}')
                    else:
                        stats['vinyl_records_created'] += 1
                        self.stdout.write(f'  Would create vinyl record: {record.get("title", "Unknown")}')
                
                if dry_run:
                    raise transaction.TransactionManagementError("Dry run - rolling back")
                    
        except transaction.TransactionManagementError:
            if not dry_run:
                raise
        except Exception as e:
            raise CommandError(f'Error during import: {e}')
        
        # Print summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('IMPORT SUMMARY'))
        self.stdout.write('='*50)
        self.stdout.write(f'Artists created: {stats["artists_created"]}')
        self.stdout.write(f'Genres created: {stats["genres_created"]}')
        self.stdout.write(f'Labels created: {stats["labels_created"]}')
        self.stdout.write(f'Vinyl records created: {stats["vinyl_records_created"]}')
        self.stdout.write(f'Vinyl records skipped (duplicates): {stats["vinyl_records_skipped"]}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - no changes were made to the database'))
            self.stdout.write('Run without --dry-run to actually import the data')
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully imported {stats["vinyl_records_created"]} vinyl records!'))
