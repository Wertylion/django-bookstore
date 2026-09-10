# user_management/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone', 'address')


class UserFeedbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label=_('Your name'),
    )
    email = forms.EmailField(
        label=_('Email'),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label=_('Message'),
    )
