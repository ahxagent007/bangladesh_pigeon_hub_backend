from django import forms
from .models import Listing
from apps.pigeons.models import Pigeon, Breed


class ListingDetailsForm(forms.ModelForm):
    """Listing fields only — pigeon is handled separately by the view."""
    class Meta:
        model = Listing
        fields = ('title', 'description', 'price', 'location', 'is_negotiable')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '1', 'min': '0'}),
        }


class QuickPigeonForm(forms.ModelForm):
    """Minimal pigeon form for inline creation on the listing page."""
    pigeon_image = forms.ImageField(
        required=False, label='Pigeon Photo',
        help_text='Main photo of your pigeon'
    )
    pedigree_image_upload = forms.ImageField(
        required=False, label='Pedigree Photo',
        help_text='Optional: photo of the pedigree certificate or chart'
    )

    class Meta:
        model = Pigeon
        fields = ('name', 'ring_number', 'breed', 'gender', 'color', 'description')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ring_number'].required = False
        self.fields['breed'].required = False
        self.fields['description'].required = False


class LegacyListingForm(forms.ModelForm):
    """Kept for backwards compatibility — used by edit flows if any."""
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
            self.fields['pigeon'].queryset = Pigeon.objects.filter(
                owner=user
            ).exclude(listing__status='active')


# Keep old name so any import that uses ListingForm still works
ListingForm = LegacyListingForm
