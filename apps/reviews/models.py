from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.vinyl.models import VinylRecord


class Review(models.Model):
    vinyl_record = models.ForeignKey(VinylRecord, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    # Review content
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Review metadata
    is_verified_purchase = models.BooleanField(default=False)  # User bought this vinyl
    helpful_count = models.PositiveIntegerField(default=0)  # Cached count of helpful votes
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vinyl_record', 'user')  # One review per user per vinyl
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vinyl_record', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.user.username}'s review of {self.vinyl_record.title}"

    def get_star_display(self):
        """Return stars as string for template display"""
        return '★' * self.rating + '☆' * (5 - self.rating)


class ReviewHelpful(models.Model):
    """Track which users found a review helpful"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(default=True)  # True for helpful, False for not helpful
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def __str__(self):
        helpful_text = "helpful" if self.is_helpful else "not helpful"
        return f"{self.user.username} found review {self.review.id} {helpful_text}"
