from crispy_forms.helper import FormHelper
from django import forms
from .models import Cart
from users.models import Address  # Modifica qui: importa da users.models
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.layout import Submit

class CartForm(forms.ModelForm):

    class Meta:
        model = Cart
        fields = ['address']  # Assuming you want to allow users to select an address for their cart

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


    street = forms.CharField(max_length=255, required=False, label="Via")
    city = forms.CharField(max_length=100, required=False, label="Città")
    postal_code = forms.CharField(max_length=20, required=False, label="CAP")


    card_number = forms.CharField(max_length=16, required=True, label="Numero carta")
    card_expiry = forms.CharField(max_length=5, required=True, label="Scadenza (MM/AA)")
    card_cvv = forms.CharField(max_length=4, required=True, label="CVV")
    nickname = forms.CharField(
        label='Nome identificativo dell\'indirizzo',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


        self.helper = FormHelper()
        self.helper.form_method = 'post'


        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user)

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
