from rest_framework import serializers
from .models import PedigreeRecord
from apps.pigeons.serializers import PigeonSerializer

class PedigreeSerializer(serializers.ModelSerializer):
    sire_detail = PigeonSerializer(source='sire', read_only=True)
    dam_detail  = PigeonSerializer(source='dam',  read_only=True)

    class Meta:
        model  = PedigreeRecord
        fields = ('id', 'pigeon', 'sire', 'sire_detail',
                  'dam', 'dam_detail', 'notes', 'is_public')
        read_only_fields = ('pigeon',)