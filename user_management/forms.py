# user_management/forms.py

from django import forms


class UserFeedbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Ваше ім\'я',
    )
    email = forms.EmailField(
        label='Email',
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label='Повідомлення',
    )
