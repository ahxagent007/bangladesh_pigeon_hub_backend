from decimal import Decimal, InvalidOperation
from django.utils import timezone
from rest_framework import generics, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Auction, Bid, AuctionWatch
from .serializers import AuctionListSerializer, AuctionDetailSerializer, BidSerializer


class AuctionListView(generics.ListAPIView):
    serializer_class   = AuctionListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'pigeon__name', 'pigeon__breed__name']
    ordering_fields    = ['end_time', 'created_at', 'bid_count']

    def get_queryset(self):
        now = timezone.now()
        # Auto-activate upcoming auctions
        Auction.objects.filter(status='upcoming', start_time__lte=now).update(status='live')

        qs = Auction.objects.select_related(
            'seller', 'pigeon__breed', 'winner'
        ).prefetch_related('gallery', 'pigeon__images')

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status__in=status_param.split(','))
        else:
            qs = qs.filter(status__in=['live', 'upcoming'])

        return qs.order_by('end_time')


class AuctionDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class   = AuctionDetailSerializer

    def get_queryset(self):
        return Auction.objects.select_related(
            'seller', 'pigeon__breed', 'winner'
        ).prefetch_related('gallery', 'pigeon__images', 'bids__bidder')

    def retrieve(self, request, *args, **kwargs):
        auction = self.get_object()
        auction.sync_status()
        auction.increment_views()
        bids = auction.bids.select_related('bidder').order_by('-created_at')[:20]
        data = self.get_serializer(auction).data
        data['bids'] = BidSerializer(bids, many=True).data
        data['min_next_bid'] = str(auction.min_next_bid)
        if request.user.is_authenticated:
            data['is_watching'] = AuctionWatch.objects.filter(
                auction=auction, user=request.user).exists()
            top = bids.first()
            data['is_top_bidder'] = bool(top and top.bidder == request.user)
        return Response(data)


class PlaceBidView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        auction = Auction.objects.get(pk=pk)
        auction.sync_status()

        if auction.seller == request.user:
            return Response({'error': "You can't bid on your own auction."}, status=400)
        if auction.status != 'live':
            return Response({'error': 'Auction is not active.'}, status=400)

        try:
            amount = Decimal(request.data.get('amount', '0'))
        except InvalidOperation:
            return Response({'error': 'Invalid amount.'}, status=400)

        if amount < auction.min_next_bid:
            return Response({'error': f'Minimum bid is BDT {auction.min_next_bid:,.0f}.'}, status=400)

        prev_top = auction.bids.order_by('-amount').first()
        Bid.objects.create(auction=auction, bidder=request.user, amount=amount)
        auction.current_price = amount
        auction.bid_count     = auction.bid_count + 1

        from datetime import timedelta
        snipe_window = timedelta(minutes=auction.anti_snipe_min)
        extended = False
        if timezone.now() > auction.end_time - snipe_window:
            auction.end_time = timezone.now() + snipe_window
            extended = True

        auction.save(update_fields=['current_price', 'bid_count', 'end_time'])

        from apps.notifications.models import notify
        if prev_top and prev_top.bidder != request.user:
            notify(prev_top.bidder, request.user, 'offer_countered',
                   f'You were outbid on "{auction.title}". New price: BDT {amount:,.0f}.',
                   f'/auctions/{pk}/')
        notify(auction.seller, request.user, 'offer_received',
               f'{request.user.username} bid BDT {amount:,.0f} on "{auction.title}".',
               f'/auctions/{pk}/dashboard/')

        return Response({
            'success': True,
            'current_price': str(amount),
            'bid_count': auction.bid_count,
            'min_bid': str(auction.min_next_bid),
            'end_time': auction.end_time.isoformat(),
            'extended': extended,
        })


class AuctionPollView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        auction = Auction.objects.get(pk=pk)
        auction.sync_status()
        top = auction.bids.order_by('-amount').first()
        return Response({
            'status':        auction.status,
            'current_price': str(auction.display_price),
            'bid_count':     auction.bid_count,
            'end_seconds':   auction.seconds_remaining,
            'end_time':      auction.end_time.isoformat(),
            'winner':        auction.winner.username if auction.winner else None,
            'top_bidder':    top.bidder.username if top else None,
            'min_bid':       str(auction.min_next_bid),
            'reserve_met':   auction.reserve_met,
        })
