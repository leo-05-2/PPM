from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='inserire un indirizzo email valido')
    class Meta:
        model = CustomUser
        # Aggiungi i campi che vuoi nel form di registrazione
        # Oltre a username e password (gestiti da UserCreationForm)
        fields = ( 'username','email')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Questo indirizzo email è già in uso.")
        return email

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'payment_method',)