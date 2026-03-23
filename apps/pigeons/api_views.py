from rest_framework import generics, permissions
from .models import Pigeon, Breed
from .serializers import PigeonSerializer, BreedSerializer

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

class BreedListView(generics.ListAPIView):
    queryset = Breed.objects.all()
    serializer_class = BreedSerializer
    permission_classes = [permissions.AllowAny]