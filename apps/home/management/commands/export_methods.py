"""
Export methods mixin for VRH data export operations.

This module contains all the export methods for different data types
(vinyl, orders, cart, reviews, wishlist) as a mixin class that can be
inherited by the main export command.
"""
import pandas as pd
from .export_helpers import dict_make_naive


class ExportMethodsMixin:
    """
    Mixin class containing all export methods for VRH data.
    
    This class provides methods to export different types of data:
    - Vinyl records with related artist, genre, and label data
    - Orders with user and order items data
    - Cart with user and cart items data
    - Reviews with user data
    - Wishlist with user and wishlist items data
    """

    def export_vinyl_data(self, writer):
        """
        Export vinyl records with related genre, artist, and label data.
        
        This method combines data from:
        - vinyl_vinylrecord table (main vinyl data)
        - vinyl_artist table (artist information)
        - vinyl_genre table (genre information)
        - vinyl_label table (label information)
        """
        self.stdout.write('Exporting vinyl records data...')
        
        # Query vinyl records with related data using select_related for efficiency
        vinyl_records = self.VinylRecord.objects.select_related(
            'artist', 'genre', 'label'
        ).all()
        
        # Convert to list of dictionaries for pandas DataFrame
        data = []
        for record in vinyl_records:
            # Create a row with all related data
            row = {
                # Vinyl record fields (main product data)
                'vinyl_id': record.id,
                'vinyl_title': record.title,
                'vinyl_release_year': record.release_year,
                'vinyl_condition': record.condition,
                'vinyl_speed': record.speed,
                'vinyl_size': record.size,
                'vinyl_weight': record.weight,
                'vinyl_price': record.price,
                'vinyl_stock_quantity': record.stock_quantity,
                'vinyl_is_available': record.is_available,
                'vinyl_description': record.description,
                'vinyl_slug': record.slug,
                'vinyl_created_at': record.created_at,
                'vinyl_updated_at': record.updated_at,
                'vinyl_featured': record.featured,
                
                # Artist fields (related artist data)
                'artist_id': record.artist.id,
                'artist_name': record.artist.name,
                'artist_type': record.artist.artist_type,
                'artist_biography': record.artist.biography,
                'artist_country': record.artist.country,
                'artist_formed_year': record.artist.formed_year,
                'artist_website': record.artist.website,
                'artist_created_at': record.artist.created_at,
                
                # Genre fields (related genre data - may be None)
                'genre_id': record.genre.id if record.genre else None,
                'genre_name': record.genre.name if record.genre else None,
                'genre_description': record.genre.description if record.genre else None,
                'genre_created_at': record.genre.created_at if record.genre else None,
                
                # Label fields (related label data - may be None)
                'label_id': record.label.id if record.label else None,
                'label_name': record.label.name if record.label else None,
                'label_country': record.label.country if record.label else None,
                'label_founded_year': record.label.founded_year if record.label else None,
                'label_website': record.label.website if record.label else None,
                'label_created_at': record.label.created_at if record.label else None,
            }
            # Convert datetime fields to timezone-naive and add to data list
            data.append(dict_make_naive(row))
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='vinyl', index=False)
        self.stdout.write(f'  - Exported {len(data)} vinyl records')

    def export_orders_data(self, writer):
        """
        Export orders with related user and order items data.
        
        This method combines data from:
        - auth_user table (user information)
        - orders_order table (order details)
        - orders_orderitem table (order line items)
        
        Creates one row per order item, with order and user data repeated.
        """
        self.stdout.write('Exporting orders data...')
        
        # Query orders with related data using select_related and prefetch_related
        orders = self.Order.objects.select_related('user').prefetch_related('items').all()
        
        # Convert to list of dictionaries for pandas DataFrame
        data = []
        for order in orders:
            # Get order items for this order
            order_items = order.items.all()
            
            if order_items.exists():
                # Create a row for each order item (one-to-many relationship)
                for item in order_items:
                    row = {
                        # User fields (repeated for each order item)
                        'user_id': order.user.id,
                        'user_username': order.user.username,
                        'user_email': order.user.email,
                        'user_first_name': order.user.first_name,
                        'user_last_name': order.user.last_name,
                        'user_is_active': order.user.is_active,
                        'user_date_joined': order.user.date_joined,
                        'user_last_login': order.user.last_login,
                        
                        # Order fields (repeated for each order item)
                        'order_id': order.id,
                        'order_uuid': order.order_id,
                        'order_email': order.email,
                        'order_first_name': order.first_name,
                        'order_last_name': order.last_name,
                        'order_phone': order.phone,
                        'order_address_line_1': order.address_line_1,
                        'order_address_line_2': order.address_line_2,
                        'order_city': order.city,
                        'order_state': order.state,
                        'order_postal_code': order.postal_code,
                        'order_country': order.country,
                        'order_status': order.status,
                        'order_total_amount': order.total_amount,
                        'order_shipping_cost': order.shipping_cost,
                        'order_notes': order.notes,
                        'order_created_at': order.created_at,
                        'order_updated_at': order.updated_at,
                        'order_shipped_at': order.shipped_at,
                        'order_delivered_at': order.delivered_at,
                        
                        # Order item fields (unique per row)
                        'item_id': item.id,
                        'item_vinyl_record_id': item.vinyl_record.id,
                        'item_quantity': item.quantity,
                        'item_price': item.price,
                        'item_vinyl_title': item.vinyl_title,
                        'item_vinyl_artist': item.vinyl_artist,
                        'item_vinyl_year': item.vinyl_year,
                        'item_created_at': item.created_at,
                    }
                    data.append(dict_make_naive(row))
            else:
                # Order with no items - still include order data with empty item fields
                row = {
                    # User fields
                    'user_id': order.user.id,
                    'user_username': order.user.username,
                    'user_email': order.user.email,
                    'user_first_name': order.user.first_name,
                    'user_last_name': order.user.last_name,
                    'user_is_active': order.user.is_active,
                    'user_date_joined': order.user.date_joined,
                    'user_last_login': order.user.last_login,
                    
                    # Order fields
                    'order_id': order.id,
                    'order_uuid': order.order_id,
                    'order_email': order.email,
                    'order_first_name': order.first_name,
                    'order_last_name': order.last_name,
                    'order_phone': order.phone,
                    'order_address_line_1': order.address_line_1,
                    'order_address_line_2': order.address_line_2,
                    'order_city': order.city,
                    'order_state': order.state,
                    'order_postal_code': order.postal_code,
                    'order_country': order.country,
                    'order_status': order.status,
                    'order_total_amount': order.total_amount,
                    'order_shipping_cost': order.shipping_cost,
                    'order_notes': order.notes,
                    'order_created_at': order.created_at,
                    'order_updated_at': order.updated_at,
                    'order_shipped_at': order.shipped_at,
                    'order_delivered_at': order.delivered_at,
                    
                    # Order item fields (empty for orders with no items)
                    'item_id': None,
                    'item_vinyl_record_id': None,
                    'item_quantity': None,
                    'item_price': None,
                    'item_vinyl_title': None,
                    'item_vinyl_artist': None,
                    'item_vinyl_year': None,
                    'item_created_at': None,
                }
                data.append(dict_make_naive(row))
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='orders', index=False)
        self.stdout.write(f'  - Exported {len(data)} order records')

    def export_cart_data(self, writer):
        """
        Export cart with related user and cart items data.
        
        This method combines data from:
        - auth_user table (user information - may be None for anonymous carts)
        - cart_cart table (cart details)
        - cart_cartitem table (cart line items)
        
        Creates one row per cart item, with cart and user data repeated.
        """
        self.stdout.write('Exporting cart data...')
        
        # Query carts with related data using select_related and prefetch_related
        carts = self.Cart.objects.select_related('user').prefetch_related('items').all()
        
        # Convert to list of dictionaries for pandas DataFrame
        data = []
        for cart in carts:
            # Get cart items for this cart
            cart_items = cart.items.all()
            
            if cart_items.exists():
                # Create a row for each cart item (one-to-many relationship)
                for item in cart_items:
                    row = {
                        # User fields (may be None for anonymous carts)
                        'user_id': cart.user.id if cart.user else None,
                        'user_username': cart.user.username if cart.user else None,
                        'user_email': cart.user.email if cart.user else None,
                        'user_first_name': cart.user.first_name if cart.user else None,
                        'user_last_name': cart.user.last_name if cart.user else None,
                        'user_is_active': cart.user.is_active if cart.user else None,
                        'user_date_joined': cart.user.date_joined if cart.user else None,
                        'user_last_login': cart.user.last_login if cart.user else None,
                        
                        # Cart fields (repeated for each cart item)
                        'cart_id': cart.id,
                        'cart_session_key': cart.session_key,
                        'cart_created_at': cart.created_at,
                        'cart_updated_at': cart.updated_at,
                        
                        # Cart item fields (unique per row)
                        'item_id': item.id,
                        'item_vinyl_record_id': item.vinyl_record.id,
                        'item_quantity': item.quantity,
                        'item_price': item.price,
                        'item_created_at': item.created_at,
                        'item_updated_at': item.updated_at,
                    }
                    data.append(dict_make_naive(row))
            else:
                # Cart with no items - still include cart data with empty item fields
                row = {
                    # User fields (may be None for anonymous carts)
                    'user_id': cart.user.id if cart.user else None,
                    'user_username': cart.user.username if cart.user else None,
                    'user_email': cart.user.email if cart.user else None,
                    'user_first_name': cart.user.first_name if cart.user else None,
                    'user_last_name': cart.user.last_name if cart.user else None,
                    'user_is_active': cart.user.is_active if cart.user else None,
                    'user_date_joined': cart.user.date_joined if cart.user else None,
                    'user_last_login': cart.user.last_login if cart.user else None,
                    
                    # Cart fields
                    'cart_id': cart.id,
                    'cart_session_key': cart.session_key,
                    'cart_created_at': cart.created_at,
                    'cart_updated_at': cart.updated_at,
                    
                    # Cart item fields (empty for carts with no items)
                    'item_id': None,
                    'item_vinyl_record_id': None,
                    'item_quantity': None,
                    'item_price': None,
                    'item_created_at': None,
                    'item_updated_at': None,
                }
                data.append(dict_make_naive(row))
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='cart', index=False)
        self.stdout.write(f'  - Exported {len(data)} cart records')

    def export_reviews_data(self, writer):
        """
        Export reviews with related user data.
        
        This method combines data from:
        - auth_user table (user information)
        - reviews_review table (review details)
        
        Creates one row per review.
        """
        self.stdout.write('Exporting reviews data...')
        
        # Query reviews with related data using select_related
        reviews = self.Review.objects.select_related('user', 'vinyl_record').all()
        
        # Convert to list of dictionaries for pandas DataFrame
        data = []
        for review in reviews:
            row = {
                # User fields (repeated for each review)
                'user_id': review.user.id,
                'user_username': review.user.username,
                'user_email': review.user.email,
                'user_first_name': review.user.first_name,
                'user_last_name': review.user.last_name,
                'user_is_active': review.user.is_active,
                'user_date_joined': review.user.date_joined,
                'user_last_login': review.user.last_login,
                
                # Review fields (unique per row)
                'review_id': review.id,
                'review_vinyl_record_id': review.vinyl_record.id,
                'review_rating': review.rating,
                'review_title': review.title,
                'review_comment': review.comment,
                'review_is_verified_purchase': review.is_verified_purchase,
                'review_created_at': review.created_at,
                'review_updated_at': review.updated_at,
            }
            data.append(dict_make_naive(row))
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='reviews', index=False)
        self.stdout.write(f'  - Exported {len(data)} review records')

    def export_wishlist_data(self, writer):
        """
        Export wishlist with related user and wishlist items data.
        
        This method combines data from:
        - auth_user table (user information)
        - wishlist_wishlist table (wishlist details)
        - wishlist_wishlistitem table (wishlist items)
        
        Creates one row per wishlist item, with wishlist and user data repeated.
        """
        self.stdout.write('Exporting wishlist data...')
        
        # Query wishlists with related data using select_related and prefetch_related
        wishlists = self.Wishlist.objects.select_related('user').prefetch_related('items').all()
        
        # Convert to list of dictionaries for pandas DataFrame
        data = []
        for wishlist in wishlists:
            # Get wishlist items for this wishlist
            wishlist_items = wishlist.items.all()
            
            if wishlist_items.exists():
                # Create a row for each wishlist item (one-to-many relationship)
                for item in wishlist_items:
                    row = {
                        # User fields (repeated for each wishlist item)
                        'user_id': wishlist.user.id,
                        'user_username': wishlist.user.username,
                        'user_email': wishlist.user.email,
                        'user_first_name': wishlist.user.first_name,
                        'user_last_name': wishlist.user.last_name,
                        'user_is_active': wishlist.user.is_active,
                        'user_date_joined': wishlist.user.date_joined,
                        'user_last_login': wishlist.user.last_login,
                        
                        # Wishlist fields (repeated for each wishlist item)
                        'wishlist_id': wishlist.id,
                        'wishlist_created_at': wishlist.created_at,
                        'wishlist_updated_at': wishlist.updated_at,
                        
                        # Wishlist item fields (unique per row)
                        'item_id': item.id,
                        'item_vinyl_record_id': item.vinyl_record.id,
                        'item_created_at': item.created_at,
                    }
                    data.append(dict_make_naive(row))
            else:
                # Wishlist with no items - still include wishlist data with empty item fields
                row = {
                    # User fields
                    'user_id': wishlist.user.id,
                    'user_username': wishlist.user.username,
                    'user_email': wishlist.user.email,
                    'user_first_name': wishlist.user.first_name,
                    'user_last_name': wishlist.user.last_name,
                    'user_is_active': wishlist.user.is_active,
                    'user_date_joined': wishlist.user.date_joined,
                    'user_last_login': wishlist.user.last_login,
                    
                    # Wishlist fields
                    'wishlist_id': wishlist.id,
                    'wishlist_created_at': wishlist.created_at,
                    'wishlist_updated_at': wishlist.updated_at,
                    
                    # Wishlist item fields (empty for wishlists with no items)
                    'item_id': None,
                    'item_vinyl_record_id': None,
                    'item_created_at': None,
                }
                data.append(dict_make_naive(row))
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='wishlist', index=False)
        self.stdout.write(f'  - Exported {len(data)} wishlist records') 