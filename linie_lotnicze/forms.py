from linie_lotnicze import models
from django import forms
from .models import *

class PasazerForm(forms.ModelForm):
    class Meta:
        model = Pasazer
        fields = ['imie', 'nazwisko']

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(max_length=255, label='Password', widget=forms.PasswordInput)

    def clean(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise ValidationError('Już istnieje użytkownik o takim loginie!')


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(max_length=255, label='Password', widget=forms.PasswordInput)
