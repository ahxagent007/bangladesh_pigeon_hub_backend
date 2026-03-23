from rest_framework import serializers
from .models import Listing
from apps.pigeons.serializers import PigeonSerializer

class ListingSerializer(serializers.ModelSerializer):
    pigeon      = PigeonSerializer(read_only=True)
    pigeon_id   = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.pigeons.models', fromlist=['Pigeon']).Pigeon.objects.all(),
        source='pigeon', write_only=True
    )
    seller_name = serializers.CharField(source='seller.username', read_only=True)

    class Meta:
        model = Listing
        fields = ('id', 'title', 'description', 'price', 'location',
                  'status', 'is_negotiable', 'views_count', 'pigeon',
                  'pigeon_id', 'seller', 'seller_name', 'created_at')
        read_only_fields = ('seller', 'views_count', 'created_at')