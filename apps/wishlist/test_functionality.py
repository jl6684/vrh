from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.vinyl.models import VinylRecord, Artist, Genre, Label
from apps.wishlist.models import Wishlist, WishlistItem
import json


class WishlistFunctionalityTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test vinyl record
        self.artist = Artist.objects.create(name='Test Artist', artist_type='band')
        self.genre = Genre.objects.create(name='Test Genre')
        self.label = Label.objects.create(name='Test Label')
        
        self.vinyl = VinylRecord.objects.create(
            title='Test Vinyl',
            artist=self.artist,
            genre=self.genre,
            label=self.label,
            price=2599,  # Price in cents
            stock_quantity=10,
            release_year=2023,
            speed='33',
            size='12'
        )

    def test_toggle_wishlist_add(self):
        """Test adding vinyl to wishlist via toggle"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('wishlist:toggle', args=[self.vinyl.id]),
            data=json.dumps({'vinyl_id': self.vinyl.id}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['in_wishlist'])
        self.assertEqual(data['action'], 'added')
        
        # Verify item was added to database
        self.assertTrue(
            WishlistItem.objects.filter(
                wishlist__user=self.user,
                vinyl_record=self.vinyl
            ).exists()
        )

    def test_toggle_wishlist_remove(self):
        """Test removing vinyl from wishlist via toggle"""
        self.client.login(username='testuser', password='testpass123')
        
        # First add item to wishlist
        wishlist, _ = Wishlist.objects.get_or_create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, vinyl_record=self.vinyl)
        
        response = self.client.post(
            reverse('wishlist:toggle', args=[self.vinyl.id]),
            data=json.dumps({'vinyl_id': self.vinyl.id}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(data['in_wishlist'])
        self.assertEqual(data['action'], 'removed')
        
        # Verify item was removed from database
        self.assertFalse(
            WishlistItem.objects.filter(
                wishlist__user=self.user,
                vinyl_record=self.vinyl
            ).exists()
        )

    def test_remove_from_wishlist(self):
        """Test removing vinyl from wishlist via remove endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add item to wishlist first
        wishlist, _ = Wishlist.objects.get_or_create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, vinyl_record=self.vinyl)
        
        response = self.client.post(
            reverse('wishlist:remove', args=[self.vinyl.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['action'], 'removed')
        
        # Verify item was removed
        self.assertFalse(
            WishlistItem.objects.filter(
                wishlist__user=self.user,
                vinyl_record=self.vinyl
            ).exists()
        )

    def test_wishlist_status(self):
        """Test wishlist status endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test when item is not in wishlist
        response = self.client.get(reverse('wishlist:status', args=[self.vinyl.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['in_wishlist'])
        
        # Add item to wishlist
        wishlist, _ = Wishlist.objects.get_or_create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, vinyl_record=self.vinyl)
        
        # Test when item is in wishlist
        response = self.client.get(reverse('wishlist:status', args=[self.vinyl.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['in_wishlist'])

    def test_unauthenticated_access(self):
        """Test that unauthenticated users can't access wishlist functions"""
        response = self.client.post(reverse('wishlist:toggle', args=[self.vinyl.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        response = self.client.get(reverse('wishlist:view'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
