"""
Django management command to export VRH data to Excel or CSV format.
Exports data from multiple tables grouped by relationships into separate worksheets/files.

Usage:
    python manage.py export_vrh_data                    # Exports to data-export/vrh_export.xlsx (Excel)
    python manage.py export_vrh_data custom_name.xlsx   # Exports to data-export/custom_name.xlsx (Excel)
    python manage.py export_vrh_data --ex-csv           # Exports to data-export/vrh_export.csv (CSV)
    python manage.py export_vrh_data custom_name.csv --ex-csv  # Exports to data-export/custom_name.csv (CSV)
    python manage.py export_vrh_data -ex-xlsx           # Explicitly export to Excel format
"""
import os, pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart, CartItem
from apps.reviews.models import Review
from apps.wishlist.models import Wishlist, WishlistItem

# Import from modular files
from .export_helpers import make_naive, dict_make_naive
from .export_methods import ExportMethodsMixin


class Command(BaseCommand, ExportMethodsMixin):
    """
    Django management command to export VRH database data to Excel or CSV format.
    
    Creates an Excel file with 5 worksheets OR separate CSV files:
    1. vinyl - Vinyl records with related artist, genre, and label data
    2. orders - Orders with user and order items data
    3. cart - Cart with user and cart items data
    4. reviews - Reviews with user data
    5. wishlist - Wishlist with user and wishlist items data
    """
    help = 'Export VRH data to Excel format with multiple worksheets or CSV format with separate files'

    def add_arguments(self, parser):
        """Define command-line arguments for the export command."""
        parser.add_argument(
            'filename',
            nargs='?',  # Make filename optional
            type=str,
            default='vrh_export.xlsx',
            help='Output filename (default: vrh_export.xlsx for Excel, vrh_export.csv for CSV)'
        )
        parser.add_argument(
            '--ex-csv',
            action='store_true',
            help='Export to CSV format instead of Excel'
        )
        parser.add_argument(
            '-ex-xlsx',
            action='store_true',
            help='Explicitly export to Excel format (default behavior)'
        )

    def handle(self, *args, **options):
        """Main execution method for the export command."""
        # Get filename and format from command line arguments
        output_filename = options['filename']
        export_csv = options['ex_csv']
        export_xlsx = options['ex_xlsx']
        
        # Determine export format and adjust filename if needed
        if export_csv:
            # CSV export mode
            if not output_filename.endswith('.csv'):
                # If filename doesn't end with .csv, add it
                if output_filename.endswith('.xlsx'):
                    output_filename = output_filename.replace('.xlsx', '.csv')
                else:
                    output_filename = output_filename + '.csv'
            export_format = 'csv'
        else:
            # Excel export mode (default)
            if not output_filename.endswith('.xlsx'):
                # If filename doesn't end with .xlsx, add it
                if output_filename.endswith('.csv'):
                    output_filename = output_filename.replace('.csv', '.xlsx')
                else:
                    output_filename = output_filename + '.xlsx'
            export_format = 'excel'
        
        # Create data-export directory path (5 levels up from this file)
        export_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
            'data-export'
        )
        
        # Create data-export directory if it doesn't exist
        os.makedirs(export_dir, exist_ok=True)
        
        # Build full output path
        output_path = os.path.join(export_dir, output_filename)
        
        # Check if file exists and inform user
        if os.path.exists(output_path):
            self.stdout.write(f'File {output_path} already exists. Overwriting...')
        else:
            self.stdout.write(f'Creating new file: {output_path}')
        
        self.stdout.write(f'Starting VRH data export to {output_path} ({export_format.upper()} format)...')
        
        # Set up model references for the mixin methods
        self.VinylRecord = VinylRecord
        self.Order = Order
        self.Cart = Cart
        self.Review = Review
        self.Wishlist = Wishlist
        
        if export_format == 'excel':
            # Excel export - create single file with multiple worksheets
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Export data to separate worksheets
                self.export_vinyl_data(writer)      # Worksheet 1: Vinyl Records
                self.export_orders_data(writer)     # Worksheet 2: Orders
                self.export_cart_data(writer)       # Worksheet 3: Cart
                self.export_reviews_data(writer)    # Worksheet 4: Reviews
                self.export_wishlist_data(writer)   # Worksheet 5: Wishlist
        else:
            # CSV export - create separate files for each data type
            base_name = output_filename.replace('.csv', '')
            
            # Export each data type to separate CSV files
            self.export_vinyl_data_csv(base_name, export_dir)      # vinyl_data.csv
            self.export_orders_data_csv(base_name, export_dir)     # orders_data.csv
            self.export_cart_data_csv(base_name, export_dir)       # cart_data.csv
            self.export_reviews_data_csv(base_name, export_dir)    # reviews_data.csv
            self.export_wishlist_data_csv(base_name, export_dir)   # wishlist_data.csv
        
        # Success message
        if export_format == 'excel':
            self.stdout.write(
                self.style.SUCCESS(f'Successfully exported VRH data to {output_path}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully exported VRH data to {export_dir} (5 CSV files)')
            ) 