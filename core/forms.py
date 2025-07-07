from crispy_forms.helper import FormHelper
from django import forms
from .models import Cart
from users.models import Address, PaymentMethod
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout
from django.core.validators import RegexValidator

class CartForm(forms.ModelForm):

    class Meta:
        model = Cart
        fields = ['address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user',None)
        super().__init__(*args, **kwargs)
        if user: self.fields['address'].queryset = Address.objects.filter(user=user)
        elif self.instance and self.instance.pk and self.instance.user:
            self.fields['address'].queryset = Address.objects.filter(user=self.instance.user)
        else:
            self.fields['address'].queryset = Address.objects.none()


        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input( Submit('submit', 'Update Cart Address'))

class CheckoutForm(forms.Form):


    use_existing_address = forms.BooleanField(
        required=False,
        initial=True,
        label="Usa un indirizzo esistente"
    )
    address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        required=False,
        label="Seleziona indirizzo"
    )

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

    use_existing_payment = forms.BooleanField(
        required=False,
        initial=True,
        label="Usa un metodo di pagamento salvato"
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),
        required=False,
        label="Metodo di pagamento salvato"
    )
    save_as_default_payment = forms.BooleanField(
        required=False,
        initial=True,
        label="Imposta come metodo di pagamento predefinito"
    )
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'use_existing_address',
            'address',  # campo address esistente
            'nickname',
            'street',
            'city',
            'postal_code',

        )
        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user)
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user)


    def clean(self):
        cleaned_data = super().clean()
        use_existing = cleaned_data.get('use_existing_address')
        if use_existing:
            address = cleaned_data.get('address')
            if not address:
                self.add_error('address', 'Seleziona un indirizzo esistente')
        else:
            required_fields = ['street', 'city', 'postal_code', 'nickname']
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'Questo campo è obbligatorio')

        if cleaned_data.get('use_existing_payment'):
            if not cleaned_data.get('payment_method'):
                self.add_error('payment_method', 'Seleziona un metodo di pagamento salvato')
        else:
            for field in ['card_number', 'card_expiry', 'card_cvv']:
                if not cleaned_data.get(field):
                    self.add_error(field, 'Questo campo è obbligatorio')





        return cleaned_data


class ShippingForm(forms.Form):
    SHIPPING_CHOICES = [
        ('standard', 'Standard (2-5 giorni): 4.99€'),
        ('express', 'Express (1-2 giorni): 9.99€'),

    ]

    shipping_method = forms.ChoiceField(
        choices=SHIPPING_CHOICES,
        widget=forms.RadioSelect,
        initial='standard',
        label='Metodo di spedizione'
    )


class CartItemQuantityForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=0,

    )

    def __init__(self, *args, **kwargs):
        self.max_quantity = kwargs.pop('max_quantity', 99)
        super().__init__(*args, **kwargs)


    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity > self.max_quantity:
            raise forms.ValidationError(f"Quantità massima disponibile: {self.max_quantity}.")
        if quantity < 0:
            raise forms.ValidationError("La quantità non può essere negativa.")

        return quantity
