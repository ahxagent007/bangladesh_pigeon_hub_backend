from rest_framework import generics, filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing, SavedListing, Offer, Payment, BD_DISTRICTS
from .serializers import ListingSerializer, OfferSerializer


# ── Listings ──────────────────────────────────────────────────────────────────

class ListingListCreateView(generics.ListCreateAPIView):
    serializer_class = ListingSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['district']
    search_fields    = ['title', 'pigeon__name', 'pigeon__breed__name', 'location']
    ordering_fields  = ['price', 'created_at', 'views_count']
    ordering         = ['-created_at']

    def get_queryset(self):
        qs = Listing.objects.filter(status='active').select_related(
            'pigeon__breed', 'seller'
        ).prefetch_related('pigeon__images', 'saved_by')
        min_p = self.request.query_params.get('min_price')
        max_p = self.request.query_params.get('max_price')
        breed = self.request.query_params.get('breed')
        if min_p:
            qs = qs.filter(price__gte=min_p)
        if max_p:
            qs = qs.filter(price__lte=max_p)
        if breed:
            qs = qs.filter(pigeon__breed__id=breed)
        return qs

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.select_related(
            'pigeon__breed', 'seller'
        ).prefetch_related('pigeon__images', 'saved_by')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        return Response(self.get_serializer(instance).data)


class MyListingsView(generics.ListAPIView):
    serializer_class   = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Listing.objects.filter(seller=self.request.user).select_related(
            'pigeon__breed').prefetch_related('pigeon__images').order_by('-created_at')


class SavedListingsView(generics.ListAPIView):
    serializer_class   = ListingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        ids = SavedListing.objects.filter(
            user=self.request.user).values_list('listing_id', flat=True)
        return Listing.objects.filter(pk__in=ids).select_related(
            'pigeon__breed', 'seller').prefetch_related('pigeon__images')


class ToggleSaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk)
        obj, created = SavedListing.objects.get_or_create(user=request.user, listing=listing)
        if not created:
            obj.delete()
        return Response({'saved': created, 'save_count': listing.saved_by.count()})


class DistrictListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response([{'value': k, 'label': v} for k, v in BD_DISTRICTS])


# ── Offers ────────────────────────────────────────────────────────────────────

class MakeOfferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        listing = Listing.objects.get(pk=pk, status='active')
        if listing.seller == request.user:
            return Response({'error': "You can't offer on your own listing."}, status=400)
        amount  = request.data.get('amount')
        message = request.data.get('message', '')
        if not amount:
            return Response({'error': 'Amount is required.'}, status=400)
        existing = Offer.objects.filter(
            listing=listing, buyer=request.user, status='pending').first()
        if existing:
            existing.amount = amount; existing.message = message; existing.save()
            offer = existing
        else:
            offer = Offer.objects.create(
                listing=listing, buyer=request.user, amount=amount, message=message)
        from apps.notifications.models import notify
        notify(listing.seller, request.user, 'offer_received',
               f'{request.user.username} made an offer of BDT {float(amount):,.0f} on "{listing.title}".', '/offers/')
        return Response(OfferSerializer(offer, context={'request': request}).data, status=201)


class MyOffersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sent = Offer.objects.filter(buyer=request.user).select_related(
            'listing__pigeon__breed', 'listing__seller').prefetch_related(
            'listing__pigeon__images').order_by('-created_at')
        received = Offer.objects.filter(listing__seller=request.user).select_related(
            'listing', 'buyer').prefetch_related('listing__pigeon__images').order_by('-created_at')
        ctx = {'request': request}
        return Response({
            'sent':     OfferSerializer(sent,     many=True, context=ctx).data,
            'received': OfferSerializer(received, many=True, context=ctx).data,
        })


class RespondOfferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, offer_id):
        offer  = Offer.objects.get(pk=offer_id, listing__seller=request.user, status='pending')
        action = request.data.get('action')
        from apps.notifications.models import notify
        if action == 'accept':
            offer.status = 'accepted'; offer.save()
            notify(offer.buyer, request.user, 'offer_accepted',
                   f'Your offer on "{offer.listing.title}" was accepted! 🎉', '/offers/')
        elif action == 'reject':
            offer.status = 'rejected'; offer.save()
            notify(offer.buyer, request.user, 'offer_rejected',
                   f'Your offer on "{offer.listing.title}" was declined.', '/offers/')
        elif action == 'counter':
            ca = request.data.get('counter_amount')
            if not ca:
                return Response({'error': 'counter_amount required.'}, status=400)
            offer.status = 'countered'; offer.counter_amount = ca
            offer.counter_msg = request.data.get('counter_msg', ''); offer.save()
            notify(offer.buyer, request.user, 'offer_countered',
                   f'Counter offer of BDT {float(ca):,.0f} on "{offer.listing.title}".', '/offers/')
        else:
            return Response({'error': 'Invalid action.'}, status=400)
        return Response(OfferSerializer(offer, context={'request': request}).data)


class SubmitPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, offer_id):
        offer  = Offer.objects.get(pk=offer_id, buyer=request.user, status='accepted')
        method = request.data.get('method', 'bkash')
        trx_id = request.data.get('trx_id', '').strip()
        if not trx_id:
            return Response({'error': 'Transaction ID is required.'}, status=400)
        Payment.objects.update_or_create(
            offer=offer,
            defaults={'buyer': request.user, 'amount': offer.amount,
                      'method': method, 'trx_id': trx_id, 'status': 'pending'})
        from apps.notifications.models import notify
        notify(offer.listing.seller, request.user, 'payment',
               f'{request.user.username} submitted {method} payment for "{offer.listing.title}".', '/offers/')
        return Response({'ok': True})