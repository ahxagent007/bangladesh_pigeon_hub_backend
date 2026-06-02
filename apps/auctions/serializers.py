from rest_framework import serializers
from .models import Auction, Bid, AuctionImage


class AuctionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AuctionImage
        fields = ('id', 'image', 'order')


class AuctionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list/home screen."""
    seller_name  = serializers.CharField(source='seller.username', read_only=True)
    display_price= serializers.ReadOnlyField()
    cover_image  = serializers.SerializerMethodField()
    pigeon_name  = serializers.CharField(source='pigeon.name', read_only=True, default=None)
    breed_name   = serializers.CharField(source='pigeon.breed.name', read_only=True, default=None)

    class Meta:
        model  = Auction
        fields = ('id', 'title', 'status', 'cover_image', 'seller_name',
                  'starting_price', 'display_price', 'bid_count', 'views_count',
                  'start_time', 'end_time', 'pigeon_name', 'breed_name')

    def get_cover_image(self, obj):
        req = self.context.get('request')
        url = obj.get_cover_image()
        if url and req and not url.startswith('http'):
            return req.build_absolute_uri(url)
        return url


class AuctionDetailSerializer(AuctionListSerializer):
    """Full serializer for auction detail page."""
    gallery = AuctionImageSerializer(many=True, read_only=True)
    pedigree_image_url = serializers.SerializerMethodField()
    winner_name  = serializers.CharField(source='winner.username', read_only=True, default=None)
    reserve_met  = serializers.ReadOnlyField()

    class Meta(AuctionListSerializer.Meta):
        fields = AuctionListSerializer.Meta.fields + (
            'description', 'reserve_price', 'min_increment', 'anti_snipe_min',
            'gallery', 'pedigree_image_url', 'winner_name', 'reserve_met',
        )

    def get_pedigree_image_url(self, obj):
        req = self.context.get('request')
        ped = obj.pedigree_image or (obj.pigeon.pedigree_image if obj.pigeon else None)
        if not ped:
            return None
        url = ped.url
        if req and not url.startswith('http'):
            return req.build_absolute_uri(url)
        return url


class BidSerializer(serializers.ModelSerializer):
    bidder_name = serializers.CharField(source='bidder.username', read_only=True)

    class Meta:
        model  = Bid
        fields = ('id', 'bidder_name', 'amount', 'created_at')
