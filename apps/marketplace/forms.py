from django import forms
from .models import Listing
from apps.pigeons.models import Pigeon

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('pigeon', 'title', 'description', 'price', 'location', 'is_negotiable')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show user's own pigeons that aren't already listed
            self.fields['pigeon'].queryset = Pigeon.objects.filter(
                owner=user
            ).exclude(listing__status='active')