# shop/forms.py

from django import forms
from .models import Rating


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'feedback': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'rating': 'Оцінка (1-5)',
            'feedback': 'Відгук',
        }
