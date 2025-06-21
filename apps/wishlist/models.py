from django.db import models
from django.contrib.auth.models import User
from apps.vinyl.models import VinylRecord


class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

    def get_total_items(self):
        return self.items.count()

    def is_empty(self):
        return self.items.count() == 0


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    vinyl_record = models.ForeignKey(VinylRecord, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'vinyl_record')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.vinyl_record.title} in {self.wishlist.user.username}'s wishlist"
