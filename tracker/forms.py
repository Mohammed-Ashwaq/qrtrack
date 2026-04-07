from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import QRCode


class QRCodeForm(forms.ModelForm):
    class Meta:
        model = QRCode
        fields = ['name', 'destination_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. Product Launch Campaign',
                'class': 'form-input',
            }),
            'destination_url': forms.URLInput(attrs={
                'placeholder': 'https://example.com',
                'class': 'form-input',
            }),
        }
        labels = {
            'name': 'QR Code Name',
            'destination_url': 'Destination URL',
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
