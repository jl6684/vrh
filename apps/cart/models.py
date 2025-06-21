from django.db import models
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous Cart ({self.session_key})"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def is_empty(self):
        return self.items.count() == 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    vinyl_record = models.ForeignKey(VinylRecord, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()  # Price at time of adding to cart
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'vinyl_record')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vinyl_record.title} x {self.quantity}"

    def get_total_price(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        # Set price from vinyl record if not already set
        if not self.price:
            self.price = self.vinyl_record.price
        super().save(*args, **kwargs)
