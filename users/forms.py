from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser, Address, PaymentMethod
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Fieldset, Field, ButtonHolder
import re
from django.core.validators import RegexValidator

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='inserire un indirizzo email valido')
    class Meta:
        model = CustomUser

        fields = ( 'username','email')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Questo indirizzo email è già in uso.")
        return email


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('phone_number', css_class='form-control'),

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
    street = forms.CharField(
        max_length=255,
        required=False,
        label="Via",
        validators=[
            RegexValidator(
                r'^[A-Za-zÀ-ÿ\s\'\-\.]+,\s*\d+[A-Za-z]?$',
                "Inserisci la via nel formato: nome via, numero civico (es. Via Roma, 12)"
            )
        ]
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        label="Città",
        validators=[RegexValidator(r'^[A-Za-z\s]+$', 'La città deve contenere solo lettere e spazi.')]
    )
    postal_code = forms.CharField(
        max_length=20,
        required=False,
        label="CAP",
        validators=[RegexValidator(r'^\d{5}$', 'Il CAP deve essere di 5 cifre numeriche.')]
    )

    nickname = forms.CharField(
        label='Nome identificativo dell\'indirizzo',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = Address
        fields = ['nickname', 'street', 'city', 'postal_code', 'country']
        help_texts = {
            'nickname': "Un nome per identificare l'indirizzo (es. Casa, Ufficio).",
            'street': "Inserisci la via e il numero civico (es. Via Roma 123).",
            'city': "La città di destinazione.",
            'postal_code': "Il CAP (es. 20121).",
            'country': "Il paese di destinazione (es. Italia).",
        }
        labels = {
            'nickname': 'Nome indirizzo',
            'street': 'Via e numero civico',
            'city': 'Città',
            'postal_code': 'CAP',
            'country': 'Paese',
        }

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

class UserProfileForm(forms.ModelForm):

    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),
        required=False,
        label="Metodo di pagamento"
    )
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('nickname'),
            Field('email'),
            Field('first_name'),
            Field('last_name'),
            Field('phone_number'),
            Field('payment_method'),
            Submit('submit', 'Salva', css_class='btn btn-primary mt-3')
        )
        if user:
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user)

class PaymentMethodForm(forms.ModelForm):
    card_number = forms.CharField(
        max_length=16,
        required=False,
        label="Numero carta",
        validators=[RegexValidator(r'^\d{16}$', 'Inserisci un numero di carta valido (16 cifre).')]
    )
    card_expiry = forms.CharField(
        max_length=5,
        required=False,
        label="Scadenza (MM/AA)",
        validators=[RegexValidator(r'^\d{2}/\d{2}$', 'Formato scadenza non valido (MM/AA).')]
    )
    card_cvv = forms.CharField(
        max_length=3,
        required=False,
        label="CVV",
        validators=[RegexValidator(r'^\d{3}$', 'CVV non valido.')]
    )
    class Meta:
        model = PaymentMethod
        fields = ['card_number', 'card_expiry', 'card_cvv']
        help_texts = {
            'card_number': 'Inserisci 16 cifre numeriche.',
            'card_expiry': 'Formato richiesto: MM/AA.',
            'card_cvv': 'Inserisci 3 cifre numeriche.',
        }

