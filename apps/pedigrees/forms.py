from django import forms
from .models import PedigreeRecord
from apps.pigeons.models import Pigeon


class PedigreeForm(forms.ModelForm):
    class Meta:
        model  = PedigreeRecord
        fields = ('sire', 'dam', 'notes', 'is_public')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, pigeon=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Only male pigeons in sire dropdown (excluding self)
        sire_qs = Pigeon.objects.filter(gender='M').select_related('breed')
        if pigeon:
            sire_qs = sire_qs.exclude(pk=pigeon.pk)
        self.fields['sire'].queryset  = sire_qs
        self.fields['sire'].required  = False
        self.fields['sire'].empty_label = '— Unknown —'

        # Only female pigeons in dam dropdown (excluding self)
        dam_qs = Pigeon.objects.filter(gender='F').select_related('breed')
        if pigeon:
            dam_qs = dam_qs.exclude(pk=pigeon.pk)
        self.fields['dam'].queryset   = dam_qs
        self.fields['dam'].required   = False
        self.fields['dam'].empty_label = '— Unknown —'