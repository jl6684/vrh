from django.db import models
from apps.vinyl.models import VinylRecord


class FeaturedVinyl(models.Model):
    """Featured vinyl records for homepage display"""
    vinyl_record = models.ForeignKey(VinylRecord, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Featured: {self.vinyl_record.title}"


class Newsletter(models.Model):
    """Newsletter subscription"""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
