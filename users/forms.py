from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser, Address
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field, ButtonHolder

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('phone_number', css_class='form-control'),
            Field('payment_method', css_class='form-control'),
            Submit('submit', 'Aggiorna Profilo', css_class='btn btn-primary mt-3')
        )


# Nuovo form di Login per Crispy Forms
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password', css_class='form-control'),
            Submit('submit', 'Login', css_class='btn btn-primary mt-3')
        )
        self.fields['username'].widget.attrs.update({'placeholder': 'Nome Utente'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['nickname', 'street', 'city', 'postal_code', 'country']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('nickname', css_class='form-control', placeholder='Es. Casa, Ufficio'),
            Field('street', css_class='form-control', placeholder='Via Roma 123'),
            Field('city', css_class='form-control', placeholder='Milano'),
            Field('postal_code', css_class='form-control', placeholder='20121'),
            Field('country', css_class='form-control', placeholder='Italia'),
            Submit('submit', 'Salva Indirizzo', css_class='btn btn-primary mt-3')
        )
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'country':
                field.initial = 'Italia'  # Puoi impostare un valore iniziale