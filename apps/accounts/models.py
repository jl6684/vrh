from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Hong Kong')
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    favorite_genres = models.ManyToManyField('vinyl.Genre', blank=True)
    
    # Profile Picture
    avatar = models.ImageField(upload_to='profile_pics/', blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def get_full_address(self):
        address_parts = [self.address_line_1]
        if self.address_line_2:
            address_parts.append(self.address_line_2)
        address_parts.extend([self.city, self.state, self.postal_code, self.country])
        return ", ".join(filter(None, address_parts))


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
