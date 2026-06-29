from django import forms

class UserFeedbackForm(forms.Form):
    username = forms.CharField(max_length = 100)
    email = forms.EmailField()
    message = forms.CharField(widget = forms.Textarea)