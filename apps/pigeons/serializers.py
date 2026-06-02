from rest_framework import serializers
from .models import Pigeon, PigeonImage, Breed

class BreedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Breed
        fields = '__all__'

class PigeonImageSerializer(serializers.ModelSerializer):
    edit_label = serializers.SerializerMethodField()

    class Meta:
        model  = PigeonImage
        fields = ('id', 'image', 'is_primary', 'caption', 'edit_score', 'edit_notes', 'edit_label')

    def get_edit_label(self, obj):
        from apps.image_auth import edit_label
        return edit_label(obj.edit_score)

class PigeonSerializer(serializers.ModelSerializer):
    images      = PigeonImageSerializer(many=True, read_only=True)
    breed_name  = serializers.CharField(source='breed.name', read_only=True)
    age_display = serializers.ReadOnlyField()
    owner_name  = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Pigeon
        fields = ('id', 'name', 'ring_number', 'gender', 'color',
                  'breed', 'breed_name', 'date_of_birth', 'age_display',
                  'weight', 'description', 'is_for_sale', 'owner',
                  'owner_name', 'images', 'created_at')
        read_only_fields = ('owner', 'created_at')