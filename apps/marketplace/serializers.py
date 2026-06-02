from rest_framework import serializers
from .models import Listing, Offer, Payment
from apps.pigeons.serializers import PigeonSerializer


class ListingSerializer(serializers.ModelSerializer):
    pigeon         = PigeonSerializer(read_only=True)
    pigeon_id      = serializers.PrimaryKeyRelatedField(
        queryset=__import__('apps.pigeons.models', fromlist=['Pigeon']).Pigeon.objects.all(),
        source='pigeon', write_only=True, required=False
    )
    seller_name    = serializers.CharField(source='seller.username', read_only=True)
    seller_id      = serializers.IntegerField(source='seller.id',    read_only=True)
    seller_avatar  = serializers.SerializerMethodField()
    district_label = serializers.CharField(source='get_district_display', read_only=True)
    is_saved       = serializers.SerializerMethodField()

    class Meta:
        model  = Listing
        fields = ('id', 'title', 'description', 'price', 'location', 'district',
                  'district_label', 'status', 'is_negotiable', 'views_count',
                  'pigeon', 'pigeon_id', 'seller', 'seller_id', 'seller_name',
                  'seller_avatar', 'is_saved', 'created_at')
        read_only_fields = ('seller', 'views_count', 'created_at')

    def get_seller_avatar(self, obj):
        req = self.context.get('request')
        if obj.seller.avatar:
            url = obj.seller.avatar.url
            if req and not url.startswith('http'):
                return req.build_absolute_uri(url)
            return url
        return None

    def get_is_saved(self, obj):
        req = self.context.get('request')
        if req and req.user.is_authenticated:
            return obj.saved_by.filter(user=req.user).exists()
        return False


class OfferSerializer(serializers.ModelSerializer):
    buyer_name     = serializers.CharField(source='buyer.username', read_only=True)
    listing_title  = serializers.CharField(source='listing.title',  read_only=True)
    listing_price  = serializers.DecimalField(
        source='listing.price', max_digits=10, decimal_places=2, read_only=True)
    listing_image  = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()

    class Meta:
        model  = Offer
        fields = ('id', 'listing', 'listing_title', 'listing_price', 'listing_image',
                  'buyer', 'buyer_name', 'amount', 'message', 'status',
                  'counter_amount', 'counter_msg', 'payment_status',
                  'created_at', 'updated_at')
        read_only_fields = ('buyer', 'status', 'counter_amount', 'counter_msg',
                            'created_at', 'updated_at')

    def get_listing_image(self, obj):
        req = self.context.get('request')
        img = obj.listing.pigeon.primary_image if obj.listing.pigeon else None
        if img:
            url = img.image.url
            if req and not url.startswith('http'):
                return req.build_absolute_uri(url)
            return url
        return None

    def get_payment_status(self, obj):
        try:
            return obj.payment.status
        except Exception:
            return None
