# shop/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Book, Rating


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'author',
            'category',
            'price',
            'published_year',
            'amount',
            'available',
            'publisher',
            'calculated_average',
        ]
        widgets = {
            'author': forms.CheckboxSelectMultiple,
            'category': forms.CheckboxSelectMultiple,
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'rating': _('Rating (1-5)'),
            'feedback': _('Feedback'),
        }
