from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Pigeon, PigeonImage, Breed
from .serializers import PigeonSerializer, PigeonImageSerializer, BreedSerializer

class PigeonListCreateView(generics.ListCreateAPIView):
    serializer_class = PigeonSerializer

    def get_queryset(self):
        return Pigeon.objects.filter(
            owner=self.request.user
        ).select_related('breed').prefetch_related('images')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PigeonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PigeonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pigeon.objects.filter(owner=self.request.user)

class PigeonImageUploadView(APIView):
    """POST /api/pigeons/<id>/images/  multipart: image, [is_primary], [caption].
    Adds an image to a pigeon the current user owns."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, pk):
        pigeon = get_object_or_404(Pigeon, pk=pk, owner=request.user)
        img = request.FILES.get('image')
        if not img:
            return Response({'error': 'image file is required.'}, status=400)

        is_primary = str(request.data.get('is_primary', 'false')).lower() in ('1', 'true', 'yes')
        # First image for a pigeon becomes primary automatically
        if not pigeon.images.exists():
            is_primary = True

        pigeon_image = PigeonImage.objects.create(
            pigeon=pigeon,
            image=img,
            is_primary=is_primary,
            caption=request.data.get('caption', ''),
        )
        return Response(
            PigeonImageSerializer(pigeon_image, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

class PigeonImageDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, image_id):
        pigeon = get_object_or_404(Pigeon, pk=pk, owner=request.user)
        image  = get_object_or_404(PigeonImage, pk=image_id, pigeon=pigeon)
        was_primary = image.is_primary
        image.delete()
        # Promote another image to primary if we removed the primary one
        if was_primary:
            nxt = pigeon.images.first()
            if nxt:
                nxt.is_primary = True
                nxt.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BreedListView(generics.ListAPIView):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [permissions.AllowAny]

class SiteStatsView(APIView):
    """GET /api/stats/ — public platform counts for the app home stats strip."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.utils import timezone
        from django.contrib.auth import get_user_model
        from apps.marketplace.models import Listing
        from apps.auctions.models import Auction

        Auction.objects.filter(
            status='upcoming', start_time__lte=timezone.now()).update(status='live')

        return Response({
            'sellers':         get_user_model().objects.filter(is_active=True).count(),
            'active_listings': Listing.objects.filter(status='active').count(),
            'live_auctions':   Auction.objects.filter(status='live').count(),
            'breeds':          Breed.objects.count(),
        })
