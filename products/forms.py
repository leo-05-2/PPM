from django import forms

class PriceFilterForm(forms.Form):
    min_price = forms.IntegerField(label='Prezzo minimo', required=False)
    max_price = forms.IntegerField(label='Prezzo massimo', required=False)

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price is not None and max_price is not None and min_price > max_price:
            raise forms.ValidationError("Il prezzo minimo non può essere maggiore del prezzo massimo.")

        return cleaned_data