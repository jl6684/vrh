from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.vinyl.models import VinylRecord
from apps.reviews.models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i} Stars') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary of your review'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Share your thoughts about this vinyl record...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].validators = [
            MinValueValidator(1),
            MaxValueValidator(5)
        ]


class ReviewSearchForm(forms.Form):
    search = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search reviews...'
        })
    )
    rating = forms.ChoiceField(
        choices=[('', 'All Ratings')] + [(i, f'{i} Stars') for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('created_at', 'Newest First'),
            ('-created_at', 'Oldest First'),
            ('rating', 'Lowest Rating'),
            ('-rating', 'Highest Rating'),
        ],
        required=False,
        initial='created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
