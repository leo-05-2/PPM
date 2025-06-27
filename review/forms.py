from django import forms
from .models import Review



class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        label='Valutazione (1-5)',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Commento',
        required=True
    )
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None or not (1 <= rating <= 5):
            raise forms.ValidationError("La valutazione deve essere un numero tra 1 e 5.")
        return rating
