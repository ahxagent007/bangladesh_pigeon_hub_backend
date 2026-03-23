from rest_framework import generics, filters, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing
from .serializers import ListingSerializer

class ListingListCreateView(generics.ListCreateAPIView):
    queryset = Listing.objects.filter(status='active').select_related(
        'pigeon__breed', 'seller'
    ).prefetch_related('pigeon__images')
    serializer_class = ListingSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pigeon__breed', 'location']
    search_fields    = ['title', 'pigeon__name', 'pigeon__breed__name']
    ordering_fields  = ['price', 'created_at']
    ordering         = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        return Response(self.get_serializer(instance).data)