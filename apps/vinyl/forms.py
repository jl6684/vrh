from django import forms
from apps.vinyl.models import VinylRecord, Genre, Artist, Label


class VinylSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, artist, or album...'
        })
    )
    
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="All Genres",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    artist = forms.ModelChoiceField(
        queryset=Artist.objects.all(),
        required=False,
        empty_label="All Artists",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    label = forms.ModelChoiceField(
        queryset=Label.objects.all(),
        required=False,
        empty_label="All Labels",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'min': '0'
        })
    )
    
    price_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'min': '0'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('title', 'Title A-Z'),
            ('-title', 'Title Z-A'),
            ('price', 'Price Low to High'),
            ('-price', 'Price High to Low'),
            ('-release_date', 'Newest First'),
            ('release_date', 'Oldest First'),
            ('-created_at', 'Recently Added'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    in_stock_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
