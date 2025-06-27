import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction, models
from django.utils.text import slugify
from django.conf import settings

from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.accounts.models import UserProfile
from apps.reviews.models import Review
from apps.orders.models import Order




class Command(BaseCommand):
    help = '''
    🎵 VINYL HOUSE - DATA MANAGER 🎵
    
    Simple and convenient data management for your vinyl shop.
    Create, clear, format, import, and export data easily.
    
    USAGE:
        python manage.py manage_data                     # Interactive mode (recommended)
        
    FEATURES:
        ⚡ Quick Start - Set up complete demo shop in one click
        📊 Statistics - View detailed database information  
        ✨ Create - Generate sample data for testing/development
        🗑️ Clear - Safely delete data with automatic backup
        🧹 Format - Clean and organize existing data
        📤 Export - Save data as CSV, JSON, or Excel files
        📥 Import - Load data from exported files
        
    Perfect for: Testing, Development, Demos, Data Management
    '''

    # Supported models
    MODELS = {
        'genre': Genre,
        'label': Label,
        'artist': Artist,
        'vinyl': VinylRecord,
        'user': User,
        'profile': UserProfile,
        'review': Review,
        'order': Order,
    }

    # Export formats
    FORMATS = ['csv', 'json', 'xlsx']

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        
        # Ensure export directory exists
        self.export_dir = Path('data_exports')
        self.export_dir.mkdir(exist_ok=True)
        
        self.show_welcome()
        self.main_menu()

    def show_welcome(self):
        """Show welcome message and current stats"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎵 VINYL HOUSE - DATA MANAGER 🎵'))
        self.stdout.write('='*60)
        self.stdout.write('Simple and convenient data management for your vinyl shop.')
        self.stdout.write('Let\'s see what you have in your database...\n')
        
        # Show current stats
        self.show_quick_stats()

    def show_quick_stats(self):
        """Show database statistics"""
        stats = {}
        for model_name, model_class in self.MODELS.items():
            stats[model_name] = model_class.objects.count()
        
        self.stdout.write('📊 Current Database:')
        self.stdout.write('-' * 25)
        for model_name, count in stats.items():
            emoji = self.get_emoji(model_name)
            self.stdout.write(f'{emoji} {model_name.capitalize()}: {count} records')
        self.stdout.write('')

    def get_emoji(self, model_name):
        """Get emoji for each model"""
        emojis = {
            'genre': '🎵', 'label': '🏷️', 'artist': '🎤', 'vinyl': '💿',
            'user': '👤', 'profile': '📋', 'review': '⭐', 'order': '🛒'
        }
        return emojis.get(model_name, '📊')

    def main_menu(self):
        """Main interactive menu"""
        while True:
            try:
                self.stdout.write('\n🚀 What would you like to do?')
                self.stdout.write('-' * 35)
                
                options = [
                    ('quickstart', '⚡ Quick Start - Set up demo shop'),
                    ('stats', '📊 View detailed statistics'),
                    ('create', '✨ Create sample data'),
                    ('clear', '🗑️ Clear data (with backup)'),
                    ('format', '🧹 Format & clean data'),
                    ('export', '📤 Export data'),
                    ('import', '📥 Import data'),
                    ('exit', '🚪 Exit')
                ]
                
                for i, (key, desc) in enumerate(options, 1):
                    self.stdout.write(f'{i}. {desc}')
                
                choice = input(f'\nEnter your choice (1-{len(options)}): ').strip()
                
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(options):
                        action = options[choice_num - 1][0]
                        
                        if action == 'exit':
                            self.stdout.write(self.style.SUCCESS('\n👋 Goodbye! Thanks for using the data manager.'))
                            break
                        elif action == 'quickstart':
                            self.quickstart_setup()
                        elif action == 'stats':
                            self.detailed_stats()
                        elif action == 'create':
                            self.create_menu()
                        elif action == 'clear':
                            self.clear_menu()
                        elif action == 'format':
                            self.format_menu()
                        elif action == 'export':
                            self.export_menu()
                        elif action == 'import':
                            self.import_menu()
                        
                        self.pause_for_user()
                        continue
                
                self.stdout.write(self.style.ERROR('❌ Please enter a valid number.'))
                
            except KeyboardInterrupt:
                self.stdout.write('\n\n👋 Goodbye!')
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))

    def detailed_stats(self):
        """Show detailed database statistics"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 DETAILED DATABASE STATISTICS')
        self.stdout.write('='*50)
        
        total_records = 0
        for model_name, model_class in self.MODELS.items():
            count = model_class.objects.count()
            total_records += count
            emoji = self.get_emoji(model_name)
            self.stdout.write(f'{emoji} {model_name.capitalize()}: {count} records')
        
        self.stdout.write(f'\n🔢 Total records: {total_records}')
        
        # Show some extra stats
        if VinylRecord.objects.exists():
            avg_price = VinylRecord.objects.aggregate(
                avg_price=models.Avg('price')
            )['avg_price']
            if avg_price:
                self.stdout.write(f'💰 Average vinyl price: ${avg_price:.2f}')

    def quickstart_setup(self):
        """Quick setup for demo vinyl shop"""
        self.stdout.write('\n' + self.style.SUCCESS('⚡ QUICK START - DEMO SHOP SETUP'))
        self.stdout.write('='*45)
        self.stdout.write('This will create a complete demo vinyl shop with:')
        self.stdout.write('  • Sample genres, labels, and artists')
        self.stdout.write('  • A collection of classic vinyl records')
        self.stdout.write('  • Demo users with profiles')
        self.stdout.write('  • Sample reviews and orders')
        self.stdout.write('\n💡 Perfect for testing, demos, or development!\n')
        
        if self.confirm('Set up demo vinyl shop?'):
            self.stdout.write('\n🚀 Setting up your demo vinyl shop...')
            
            # Create all sample data with reasonable amounts
            models = list(self.MODELS.keys())
            created = {}
            
            # Create basic data first
            created['genre'] = self.create_genres()
            created['label'] = self.create_labels()
            created['artist'] = self.create_artists(10)  # 10 artists
            created['vinyl'] = self.create_vinyl_records(8)  # All available vinyl
            created['user'] = self.create_users(5)  # 5 demo users
            created['profile'] = self.create_profiles()  # Profiles for all users
            created['review'] = self.create_reviews(15)  # 15 reviews
            created['order'] = self.create_orders(10)  # 10 orders
            
            # Summary
            total_created = sum(created.values())
            if total_created > 0:
                self.stdout.write(self.style.SUCCESS(f'\n🎉 Demo shop setup complete!'))
                self.stdout.write('\n📈 Created:')
                for model_name, count in created.items():
                    if count > 0:
                        emoji = self.get_emoji(model_name)
                        self.stdout.write(f'   {emoji} {count} {model_name}(s)')
                
                # Show current stats
                self.stdout.write('\n📊 Your shop now has:')
                self.show_quick_stats()
            else:
                self.stdout.write(self.style.WARNING('\n💭 Demo shop already set up!'))
                self.stdout.write('Use the "Create sample data" option to add more records.')

    def create_menu(self):
        """Create sample data menu"""
        self.stdout.write('\n' + self.style.SUCCESS('✨ CREATE SAMPLE DATA'))
        self.stdout.write('='*40)
        self.stdout.write('Create sample data for your vinyl shop.\n')
        
        # Select models
        models = self.select_models('Which data would you like to create?')
        if not models:
            return
        
        # Get count
        count = self.get_record_count()
        
        # Confirm
        self.stdout.write(f'\n📋 Ready to create:')
        self.stdout.write(f'   • Models: {", ".join(models)}')
        self.stdout.write(f'   • Count: {count} records per model')
        
        if self.confirm('Create sample data?'):
            self.create_sample_data(models, count)

    def clear_menu(self):
        """Clear data menu"""
        self.stdout.write('\n' + self.style.ERROR('🗑️ CLEAR DATA'))
        self.stdout.write('='*40)
        self.stdout.write(self.style.WARNING('⚠️ This will permanently delete data!'))
        self.stdout.write('A backup will be created automatically.\n')
        
        # Show quick reset option first
        total_records = sum(model.objects.count() for model in self.MODELS.values())
        if total_records > 0:
            self.stdout.write('💥 Quick option:')
            self.stdout.write(f'0. 🔄 Reset Everything ({total_records} total records)')
            self.stdout.write('')
        
        # Select models
        models = self.select_models('Which data would you like to clear?')
        
        # Handle reset all if no models selected but user wants to reset
        if not models:
            if total_records > 0:
                choice = input('\nEnter "0" to reset everything, or press Enter to cancel: ').strip()
                if choice == '0':
                    if self.confirm_dangerous('DELETE ALL vinyl shop data? (backup will be created)'):
                        models = list(self.MODELS.keys())
                    else:
                        return
                else:
                    return
            else:
                return
        
        if not models:
            return
        
        # Show what will be deleted
        total = 0
        self.stdout.write('📊 Records to be deleted:')
        for model_name in models:
            count = self.MODELS[model_name].objects.count()
            total += count
            emoji = self.get_emoji(model_name)
            self.stdout.write(f'   {emoji} {model_name.capitalize()}: {count} records')
        
        self.stdout.write(f'\n💥 TOTAL: {total} records will be deleted')
        
        if total == 0:
            self.stdout.write('✅ No data to clear!')
            return
        
        if self.confirm_dangerous('DELETE this data? (backup will be created)'):
            self.clear_data(models)

    def format_menu(self):
        """Format data menu"""
        self.stdout.write('\n' + self.style.SUCCESS('🧹 FORMAT & CLEAN DATA'))
        self.stdout.write('='*40)
        self.stdout.write('Clean and standardize your existing data (non-destructive).\n')
        self.stdout.write('💡 This will improve data quality by:')
        self.stdout.write('   • Removing extra spaces from names')
        self.stdout.write('   • Standardizing capitalization (Title Case)')
        self.stdout.write('   • Cleaning email addresses (lowercase)')
        self.stdout.write('   • Generating missing slugs')
        self.stdout.write('   • Fixing formatting inconsistencies')
        self.stdout.write('\n🔒 Safe operation - no data will be deleted!\n')
        
        models = self.select_models('Which data would you like to format?')
        if not models:
            return
        
        # Ask if user wants to see detailed changes
        show_details = input('\n👁️ Show detailed changes? (y/n, default=n): ')

        if self.confirm('Format and clean the selected data?'):
            # Temporarily increase verbosity if user wants details
            original_verbosity = self.verbosity
            if show_details:
                self.verbosity = 2
            
            self.format_data(models)
            
            # Restore original verbosity
            self.verbosity = original_verbosity

    def export_menu(self):
        """Export data menu"""
        self.stdout.write('\n' + self.style.SUCCESS('📤 EXPORT DATA'))
        self.stdout.write('='*40)
        self.stdout.write('Export your data for backup or analysis.\n')
        
        # Select models
        models = self.select_models('Which data would you like to export?')
        if not models:
            return
        
        # Select format
        format_choice = self.select_format()
        if not format_choice:
            return
        
        if self.confirm(f'Export data in {format_choice.upper()} format?'):
            self.export_data(models, format_choice)

    def import_menu(self):
        """Import data menu"""
        self.stdout.write('\n' + self.style.SUCCESS('📥 IMPORT DATA'))
        self.stdout.write('='*40)
        self.stdout.write('Import data from exported files.\n')
        self.stdout.write(f'📁 Looking in: {self.export_dir.absolute()}\n')
        
        # Get all export and backup folders
        export_folders = [d for d in self.export_dir.iterdir() if d.is_dir()]
        individual_files = [f for f in self.export_dir.iterdir() if f.is_file() and f.name != '.DS_Store']
        
        if not export_folders and not individual_files:
            self.stdout.write('❌ No import files found in data_exports/ directory.')
            self.stdout.write('💡 Tips:')
            self.stdout.write('   • Create exports first using the Export menu')
            self.stdout.write('   • Place JSON/CSV files directly in data_exports/')
            self.stdout.write('   • Use backup folders from previous operations')
            return
        
        all_options = []
        
        # Show export folders first
        if export_folders:
            self.stdout.write('📂 Export/Backup Folders:')
            for folder in sorted(export_folders):
                files_in_folder = list(folder.glob('*.json')) + list(folder.glob('*.csv'))
                if files_in_folder:
                    folder_type = "📤 Export" if folder.name.startswith('export_') else "🛡️ Backup"
                    self.stdout.write(f'{len(all_options)+1}. {folder_type}: {folder.name} ({len(files_in_folder)} files)')
                    all_options.append(('folder', folder))
        
        # Show individual files
        if individual_files:
            self.stdout.write('\n📄 Individual Files:')
            for file in sorted(individual_files):
                self.stdout.write(f'{len(all_options)+1}. 📄 {file.name}')
                all_options.append(('file', file))
        
        if not all_options:
            self.stdout.write('❌ No valid import files found.')
            return
        
        try:
            choice = int(input(f'\nSelect option (1-{len(all_options)}): '))
            if 1 <= choice <= len(all_options):
                option_type, selected_item = all_options[choice - 1]
                
                if option_type == 'folder':
                    self.import_from_folder(selected_item)
                else:
                    if self.confirm(f'Import data from {selected_item.name}?'):
                        self.import_data(selected_item)
        except (ValueError, IndexError):
            self.stdout.write('❌ Invalid selection.')

    def import_from_folder(self, folder):
        """Import all files from a folder"""
        files = list(folder.glob('*.json')) + list(folder.glob('*.csv'))
        if not files:
            self.stdout.write('❌ No importable files in folder.')
            return
        
        # Sort files for consistent ordering
        files = sorted(files, key=lambda f: f.name)
        
        self.stdout.write(f'\n📂 Files in {folder.name}:')
        for i, file in enumerate(files, 1):
            self.stdout.write(f'{i}. {file.name}')
        
        choice = input(f'\nOptions:\n'
                      f'  • Enter number (1-{len(files)}) for specific file\n'
                      f'  • Enter "all" to import all files\n'
                      f'  • Press Enter to cancel\n'
                      f'Choice: ').strip().lower()
        
        if choice == 'all':
            if self.confirm(f'Import all {len(files)} files from {folder.name}?'):
                for file in files:
                    self.stdout.write(f'\n📥 Importing {file.name}...')
                    self.import_data(file)
        elif choice.isdigit():
            file_idx = int(choice) - 1
            if 0 <= file_idx < len(files):
                selected_file = files[file_idx]
                if self.confirm(f'Import {selected_file.name}?'):
                    self.import_data(selected_file)
            else:
                self.stdout.write('❌ Invalid file number.')
        elif choice == '':
            return  # Cancel
        else:
            self.stdout.write('❌ Invalid choice.')

    def select_models(self, question):
        """Interactive model selection"""
        self.stdout.write(f'{question}')
        self.stdout.write('-' * len(question))
        
        model_list = list(self.MODELS.keys())
        for i, model_name in enumerate(model_list, 1):
            count = self.MODELS[model_name].objects.count()
            emoji = self.get_emoji(model_name)
            self.stdout.write(f'{i}. {emoji} {model_name.capitalize()} ({count} records)')
        
        self.stdout.write(f'{len(model_list) + 1}. 🌟 All models')
        
        try:
            choices = input(f'\nEnter numbers (1-{len(model_list) + 1}) or comma-separated: ').strip()
            
            if choices == str(len(model_list) + 1):
                return list(self.MODELS.keys())
            
            selected = []
            for choice in choices.split(','):
                choice = choice.strip()
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(model_list):
                        selected.append(model_list[idx])
            
            return selected if selected else None
            
        except (ValueError, KeyboardInterrupt):
            return None

    def select_format(self):
        """Select export format"""
        self.stdout.write('📁 Choose export format:')
        formats = [
            ('csv', '📄 CSV - Excel compatible, good for analysis'),
            ('json', '📋 JSON - Technical format, preserves data types'),
            ('xlsx', '📊 Excel - Professional reports with formatting')
        ]
        
        for i, (fmt, desc) in enumerate(formats, 1):
            self.stdout.write(f'{i}. {desc}')
        
        try:
            choice = int(input('\nEnter choice (1-3): '))
            if 1 <= choice <= 3:
                return formats[choice - 1][0]
        except ValueError:
            pass
        
        return None

    def get_record_count(self):
        """Get number of records to create"""
        self.stdout.write('🔢 How many records per model?')
        self.stdout.write('Suggestions:')
        self.stdout.write('  • Testing: 5-10 records')
        self.stdout.write('  • Development: 20-50 records')
        self.stdout.write('  • Demo: 50-100 records')
        
        try:
            count = int(input('\nEnter count (default 25): ') or '25')
            return max(1, min(count, 200))  # Limit between 1-200
        except ValueError:
            return 25

    def confirm(self, message):
        """Simple confirmation"""
        response = input(f'\n✅ {message} (y/n): ').strip().lower()
        return response in ['y', 'yes']

    def confirm_dangerous(self, message):
        """Extra confirmation for dangerous operations"""
        self.stdout.write(f'\n⚠️ DANGER: {message}')
        response = input('Type "DELETE" to confirm: ').strip()
        if response == 'DELETE':
            return input('Are you absolutely sure? (yes/no): ').strip().lower() == 'yes'
        return False

    def pause_for_user(self):
        """Pause for user to read output"""
        input('\nPress Enter to continue...')

    # Data operation methods
    def create_sample_data(self, models, count):
        """Create sample data"""
        self.stdout.write(f'\n🚀 Creating sample data...')
        self.stdout.write('💡 Note: Existing records won\'t be duplicated')
        
        created = {}
        for model_name in models:
            self.stdout.write(f'\n📋 Creating {model_name} data...')
            
            if model_name == 'genre':
                created[model_name] = self.create_genres()
            elif model_name == 'label':
                created[model_name] = self.create_labels()
            elif model_name == 'artist':
                created[model_name] = self.create_artists(count)
            elif model_name == 'vinyl':
                created[model_name] = self.create_vinyl_records(count)
            elif model_name == 'user':
                created[model_name] = self.create_users(count)
            elif model_name == 'profile':
                created[model_name] = self.create_profiles()
            elif model_name == 'review':
                created[model_name] = self.create_reviews(count)
            elif model_name == 'order':
                created[model_name] = self.create_orders(count)
        
        # Summary
        total_created = sum(created.values())
        if total_created > 0:
            self.stdout.write(self.style.SUCCESS(f'\n🎉 Sample data created successfully!'))
            for model_name, count in created.items():
                emoji = self.get_emoji(model_name)
                if count > 0:
                    self.stdout.write(f'{emoji} {model_name.capitalize()}: {count} new records')
        else:
            self.stdout.write(self.style.WARNING('\n💭 No new records created (all sample data already exists)'))

    def clear_data(self, models):
        """Clear data with backup"""
        # Create backup first
        self.stdout.write('🛡️ Creating backup before deletion...')
        backup_dir = self.export_dir / f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        backup_dir.mkdir(exist_ok=True)
        
        for model_name in self.MODELS.keys():
            self.export_model_data(model_name, 'json', backup_dir)
        
        self.stdout.write(f'✅ Backup created: {backup_dir}')
        
        # Delete data in correct order (reverse dependencies)
        deletion_order = ['order', 'review', 'vinyl', 'profile', 'user', 'artist', 'label', 'genre']
        
        total_deleted = 0
        for model_name in deletion_order:
            if model_name in models:
                count = self.MODELS[model_name].objects.count()
                self.MODELS[model_name].objects.all().delete()
                total_deleted += count
                if count > 0:
                    self.stdout.write(f'🗑️ Deleted {count} {model_name} records')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Cleared {total_deleted} total records'))

    def format_data(self, models):
        """Format and clean data"""
        self.stdout.write('🧹 Formatting and cleaning data...\n')
        
        total_changes = 0
        for model_name in models:
            self.stdout.write(f'📋 Formatting {model_name} data...')
            changes = self.format_model_data(model_name)
            total_changes += changes
            
            if changes > 0:
                self.stdout.write(f'   ✅ Made {changes} improvements to {model_name}')
            else:
                self.stdout.write(f'   ✅ {model_name.capitalize()} data already clean')
        
        if total_changes > 0:
            self.stdout.write(self.style.SUCCESS(f'\n🎉 Total improvements: {total_changes} formatting fixes'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ All data was already properly formatted'))

    def export_data(self, models, format_choice):
        """Export data"""
        self.stdout.write(f'📤 Exporting data in {format_choice.upper()} format...')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_folder = self.export_dir / f'export_{timestamp}'
        export_folder.mkdir(exist_ok=True)
        
        exported_files = []
        for model_name in models:
            file_path = self.export_model_data(model_name, format_choice, export_folder)
            if file_path:
                exported_files.append(file_path)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Exported {len(exported_files)} files to: {export_folder}'))
        for file_path in exported_files:
            self.stdout.write(f'   📄 {file_path.name}')

    def import_data(self, file_path):
        """Import data from file"""
        self.stdout.write(f'📥 Importing data from {file_path.name}...')
        # This would implement file import logic
    def import_data(self, file_path):
        """Import data from file"""
        self.stdout.write(f'📥 Importing from: {file_path.name}')
        
        if file_path.suffix.lower() == '.json':
            self.import_json(file_path)
        elif file_path.suffix.lower() == '.csv':
            self.import_csv(file_path)
        else:
            self.stdout.write('🚧 Import functionality for this format coming soon!')
            self.stdout.write('💡 Supported formats: JSON (from exports), CSV')

    def import_json(self, file_path):
        """Import JSON data (Django format)"""
        try:
            from django.core import serializers
            with open(file_path, 'r', encoding='utf-8') as jsonfile:
                data = jsonfile.read()
                objects = list(serializers.deserialize('json', data))
                
                if not objects:
                    self.stdout.write('⚠️ No data found in file.')
                    return
                
                created = 0
                updated = 0
                skipped = 0
                
                for obj in objects:
                    try:
                        # Check if object already exists
                        model_class = obj.object.__class__
                        existing = None
                        
                        if hasattr(obj.object, 'pk') and obj.object.pk:
                            try:
                                existing = model_class.objects.get(pk=obj.object.pk)
                            except model_class.DoesNotExist:
                                existing = None
                        
                        # Save the object
                        obj.save()
                        
                        if existing:
                            updated += 1
                        else:
                            created += 1
                            
                    except Exception as e:
                        skipped += 1
                        if self.verbosity >= 2:
                            self.stdout.write(f'⚠️ Skipped: {str(e)}')
                        continue
                
                self.stdout.write(self.style.SUCCESS(f'✅ Import complete!'))
                if created > 0:
                    self.stdout.write(f'   📥 Created: {created} new records')
                if updated > 0:
                    self.stdout.write(f'   🔄 Updated: {updated} existing records')
                if skipped > 0:
                    self.stdout.write(f'   ⚠️ Skipped: {skipped} records (errors)')
                    
                total_processed = created + updated
                if total_processed == 0:
                    self.stdout.write('💭 No changes made - all data was already current')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Import failed: {str(e)}'))

    def import_csv(self, file_path):
        """Simple CSV import notification"""
        self.stdout.write('📄 CSV Import (Basic)')
        self.stdout.write(f'📥 File: {file_path.name}')
        self.stdout.write('💡 CSV import is currently disabled for complex data with foreign keys.')
        self.stdout.write('💡 Use JSON import for full data restoration with relationships.')
        self.stdout.write('✨ For simple data (genres, labels), you can manually create them first.')

    # Sample data creation methods
    def create_genres(self):
        """Create sample genres"""
        genres_data = [
            ('Rock', 'Classic rock and modern rock music'),
            ('Jazz', 'Smooth jazz and contemporary jazz'),
            ('Electronic', 'Electronic dance music and ambient'),
            ('Hip Hop', 'Urban hip hop and rap music'),
            ('Pop', 'Popular mainstream music'),
            ('Classical', 'Classical orchestral music'),
            ('Blues', 'Traditional and modern blues'),
            ('Country', 'Country and western music'),
            ('Reggae', 'Reggae and Caribbean music'),
            ('Folk', 'Traditional folk music'),
        ]
        
        created = 0
        for name, description in genres_data:
            genre, created_flag = Genre.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created_flag:
                created += 1
        
        return created

    def create_labels(self):
        """Create sample record labels"""
        labels_data = [
            ('Motown Records', 'United States', 1959),
            ('Blue Note Records', 'United States', 1939),
            ('Atlantic Records', 'United States', 1947),
            ('Columbia Records', 'United States', 1887),
            ('Capitol Records', 'United States', 1942),
            ('Chess Records', 'United States', 1950),
            ('Stax Records', 'United States', 1957),
            ('Def Jam Recordings', 'United States', 1984),
            ('Island Records', 'United Kingdom', 1959),
            ('Virgin Records', 'United Kingdom', 1972),
        ]
        
        created = 0
        for name, country, founded_year in labels_data:
            label, created_flag = Label.objects.get_or_create(
                name=name,
                defaults={'country': country, 'founded_year': founded_year}
            )
            if created_flag:
                created += 1
        
        return created

    def create_artists(self, count=15):
        """Create sample artists"""
        artists_data = [
            ('Stevie Wonder', 'male', 'United States', 1950),
            ('Aretha Franklin', 'female', 'United States', 1942),
            ('The Beatles', 'band', 'United Kingdom', 1960),
            ('Miles Davis', 'male', 'United States', 1926),
            ('Joni Mitchell', 'female', 'Canada', 1943),
            ('Bob Dylan', 'male', 'United States', 1941),
            ('Prince', 'male', 'United States', 1958),
            ('Nina Simone', 'female', 'United States', 1933),
            ('David Bowie', 'male', 'United Kingdom', 1947),
            ('Billie Holiday', 'female', 'United States', 1915),
            ('John Coltrane', 'male', 'United States', 1926),
            ('Led Zeppelin', 'band', 'United Kingdom', 1968),
            ('Marvin Gaye', 'male', 'United States', 1939),
            ('Diana Ross', 'female', 'United States', 1944),
            ('The Rolling Stones', 'band', 'United Kingdom', 1962),
            ('Ella Fitzgerald', 'female', 'United States', 1917),
            ('Ray Charles', 'male', 'United States', 1930),
            ('Tina Turner', 'female', 'United States', 1939),
            ('Pink Floyd', 'band', 'United Kingdom', 1965),
            ('Whitney Houston', 'female', 'United States', 1963),
        ]
        
        created = 0
        for name, artist_type, country, formed_year in artists_data[:count]:
            artist, created_flag = Artist.objects.get_or_create(
                name=name,
                defaults={
                    'artist_type': artist_type,
                    'country': country,
                    'formed_year': formed_year,
                    'biography': f'Legendary {artist_type} from {country}.'
                }
            )
            if created_flag:
                created += 1
        
        return created

    def create_vinyl_records(self, count=20):
        """Create sample vinyl records"""
        import random
        
        # Ensure we have some basic data first
        if not Genre.objects.exists():
            self.create_genres()
        if not Label.objects.exists():
            self.create_labels()
        if not Artist.objects.exists():
            self.create_artists()
        
        vinyl_data = [
            ('Songs in the Key of Life', 1976, 30),
            ('What\'s Going On', 1971, 25),
            ('Abbey Road', 1969, 28),
            ('Kind of Blue', 1959, 33),
            ('Blue', 1971, 27),
            ('Highway 61 Revisited', 1965, 26),
            ('Purple Rain', 1984, 29),
            ('Pastel Blues', 1965, 32),
            ('The Rise and Fall of Ziggy Stardust', 1972, 31),
            ('Lady in Satin', 1958, 36),
            ('A Love Supreme', 1965, 34),
            ('Led Zeppelin IV', 1971, 30),
            ('Let\'s Get It On', 1973, 24),
            ('Diana Ross', 1970, 23),
            ('Sticky Fingers', 1971, 29),
            ('Ella Fitzgerald Sings the Cole Porter Song Book', 1956, 37),
            ('The Genius of Ray Charles', 1959, 25),
            ('Private Dancer', 1984, 22),
            ('The Dark Side of the Moon', 1973, 32),
            ('Whitney Houston', 1985, 20),
        ]
        
        artists = list(Artist.objects.all())
        genres = list(Genre.objects.all())
        labels = list(Label.objects.all())
        
        if not artists or not genres or not labels:
            return 0
        
        created = 0
        for title, release_year, price in vinyl_data[:count]:
            # Check if record already exists
            if not VinylRecord.objects.filter(title=title).exists():
                vinyl = VinylRecord.objects.create(
                    title=title,
                    artist=random.choice(artists),
                    genre=random.choice(genres),
                    label=random.choice(labels),
                    release_year=release_year,
                    price=price,
                    stock_quantity=random.randint(1, 10),
                    condition=random.choice(['mint', 'near_mint', 'very_good_plus', 'very_good']),
                    description=f'Classic album "{title}" from {release_year}. A must-have for any vinyl collection.'
                )
                created += 1
        
        return created

    def create_users(self, count=5):
        """Create sample users"""
        import random
        
        users_data = [
            ('vinylcollector', 'collector@example.com', 'John', 'Smith'),
            ('musiclover', 'music@example.com', 'Jane', 'Doe'),
            ('jazzfan', 'jazz@example.com', 'Mike', 'Johnson'),
            ('rockhound', 'rock@example.com', 'Sarah', 'Wilson'),
            ('soulseeker', 'soul@example.com', 'David', 'Brown'),
            ('bluesbrother', 'blues@example.com', 'Lisa', 'Davis'),
            ('funkmaster', 'funk@example.com', 'Tom', 'Miller'),
            ('discoking', 'disco@example.com', 'Amy', 'Garcia'),
        ]
        
        created = 0
        for username, email, first_name, last_name in users_data[:count]:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password='password123'  # In real apps, use proper password handling
                )
                created += 1
        
        return created

    def create_profiles(self):
        """Create profiles for users without them"""
        created = 0
        for user in User.objects.filter(userprofile__isnull=True):
            UserProfile.objects.create(
                user=user,
                bio=f'Passionate music lover and vinyl collector.',
                birth_date=date(1990, 1, 1),  # Default birth date
            )
            created += 1
        
        return created

    def create_reviews(self, count=10):
        """Create sample reviews"""
        import random
        
        if not VinylRecord.objects.exists() or not User.objects.exists():
            return 0
        
        review_texts = [
            "Amazing album! The sound quality is incredible.",
            "Classic record that never gets old. Highly recommended!",
            "Great pressing quality and excellent packaging.",
            "This vinyl sounds much better than the digital version.",
            "A masterpiece that belongs in every collection.",
            "Outstanding performance and crystal clear audio.",
            "Worth every penny. Fantastic addition to my collection.",
            "The best pressing I've heard of this album.",
            "Excellent condition and fast shipping.",
            "One of the greatest albums of all time on vinyl.",
        ]
        
        vinyls = list(VinylRecord.objects.all())
        users = list(User.objects.all())
        
        created = 0
        for _ in range(min(count, len(vinyls) * len(users))):
            vinyl = random.choice(vinyls)
            user = random.choice(users)
            
            # Avoid duplicate reviews
            if not Review.objects.filter(vinyl_record=vinyl, user=user).exists():
                Review.objects.create(
                    vinyl_record=vinyl,
                    user=user,
                    rating=random.randint(3, 5),  # Good to excellent ratings
                    comment=random.choice(review_texts)
                )
                created += 1
        
        return created

    def create_orders(self, count=5):
        """Create sample orders"""
        import random
        
        if not VinylRecord.objects.exists() or not User.objects.exists():
            return 0
        
        vinyls = list(VinylRecord.objects.all())
        users = list(User.objects.all())
        
        created = 0
        for _ in range(count):
            user = random.choice(users)
            vinyl = random.choice(vinyls)
            quantity = random.randint(1, 3)
            
            order = Order.objects.create(
                user=user,
                total_amount=vinyl.price * quantity,
                status=random.choice(['pending', 'processing', 'shipped', 'delivered']),
                shipping_address=f"{random.randint(100, 999)} Music St, Vinyl City, VC {random.randint(10000, 99999)}"
            )
            created += 1
        
        return created
