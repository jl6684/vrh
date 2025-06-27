from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = '''
    🚀 VINYL HOUSE - QUICK START
    
    Super fast setup for your vinyl shop demo.
    This is a shortcut that runs the main data manager in Quick Start mode.
    
    USAGE:
        python manage.py quickstart          # Set up demo shop instantly
        python manage.py manage_data         # Full interactive mode
    '''

    def handle(self, *args, **options):
        self.stdout.write('🚀 Quick Start - Setting up your vinyl shop...')
        self.stdout.write('This will run the data manager in Quick Start mode.\n')
        
        # Call the main command in interactive mode
        # User can select Quick Start from the menu
        call_command('manage_data')
