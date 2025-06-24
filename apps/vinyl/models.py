from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=200, unique=True)
    country = models.CharField(max_length=100, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Artist(models.Model):
    ARTIST_TYPE_CHOICES = [
        ('male', 'Male Artist'),
        ('female', 'Female Artist'),
        ('band', 'Band'),
        ('assortment', 'Assortment'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    artist_type = models.CharField(max_length=20, choices=ARTIST_TYPE_CHOICES, default='other')
    biography = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    formed_year = models.PositiveIntegerField(null=True, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class VinylRecord(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('near_mint', 'Near Mint'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('fair', 'Fair'),
    ]

    SPEED_CHOICES = [
        ('33', '33 1/3 RPM'),
        ('45', '45 RPM'),
        ('78', '78 RPM'),
    ]

    SIZE_CHOICES = [
        ('7', '7"'),
        ('10', '10"'),
        ('12', '12"'),
    ]

    # Basic Information
    title = models.CharField(max_length=300)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='vinyl_records')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Vinyl Specifications
    release_year = models.PositiveIntegerField()
    
    # Physical Details
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='new')
    speed = models.CharField(max_length=5, choices=SPEED_CHOICES, default='33')
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, default='12')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # in grams
    
    # Pricing and Inventory
    price = models.PositiveIntegerField()
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    
    # Media Files
    cover_image = models.ImageField(upload_to='vinyl_covers/', blank=True)
    audio_sample = models.FileField(upload_to='audio_samples/', blank=True)
    
    # SEO and Description
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=350, unique=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['artist', 'title']),
            models.Index(fields=['genre']),
            models.Index(fields=['price']),
            models.Index(fields=['release_year']),
        ]

    def __str__(self):
        return f"{self.artist.name} - {self.title} ({self.release_year})"

    def get_absolute_url(self):
        return reverse('vinyl:detail', kwargs={'slug': self.slug})

    def is_in_stock(self):
        return self.stock_quantity > 0 and self.is_available

    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_review_count(self):
        return self.reviews.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(f"{self.artist.name}-{self.title}-{self.release_year}")
            slug = base_slug
            counter = 1
            while VinylRecord.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
