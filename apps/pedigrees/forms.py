from django import forms
from .models import PedigreeRecord
from apps.pigeons.models import Pigeon

class PedigreeForm(forms.ModelForm):
    class Meta:
        model = PedigreeRecord
        fields = ('sire', 'dam', 'notes', 'is_public')
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, pigeon=None, **kwargs):
        super().__init__(*args, **kwargs)
        if pigeon:
            # Exclude the pigeon itself to prevent circular references
            self.fields['sire'].queryset = Pigeon.objects.exclude(pk=pigeon.pk)
            self.fields['dam'].queryset  = Pigeon.objects.exclude(pk=pigeon.pk)
        self.fields['sire'].required = False
        self.fields['dam'].required  = False