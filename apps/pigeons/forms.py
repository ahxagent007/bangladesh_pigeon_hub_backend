from django import forms
from .models import Pigeon, PigeonImage

class PigeonForm(forms.ModelForm):
    class Meta:
        model = Pigeon
        fields = (
            'name', 'ring_number', 'breed', 'gender',
            'color', 'date_of_birth', 'weight', 'description'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'description':   forms.Textarea(attrs={'rows': 3}),
            'weight':        forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
        }

class PigeonImageForm(forms.Form):
    image = forms.ImageField(required=False)