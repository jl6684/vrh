from django.db import models
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    # Order identification
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Customer information
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    
    # Shipping address
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Hong Kong')
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.PositiveIntegerField()
    shipping_cost = models.PositiveIntegerField(default=0)
    
    # Notes and special instructions
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['order_id']),
        ]

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"

    @property
    def order_number(self):
        """Return order_id as order_number for compatibility"""
        return str(self.order_id)[:8].upper()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_address(self):
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.extend([self.city, self.state, self.postal_code, self.country])
        return ", ".join(filter(None, address_parts))

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    vinyl_record = models.ForeignKey(VinylRecord, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()  # Price at time of purchase
    
    # Snapshot of vinyl details at time of purchase
    vinyl_title = models.CharField(max_length=300)
    vinyl_artist = models.CharField(max_length=200)
    vinyl_year = models.PositiveIntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.vinyl_title} x {self.quantity}"

    def get_total_price(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        # Store snapshot of vinyl details
        if not self.vinyl_title:
            self.vinyl_title = self.vinyl_record.title
            self.vinyl_artist = self.vinyl_record.artist.name
            self.vinyl_year = self.vinyl_record.release_year
        super().save(*args, **kwargs)
