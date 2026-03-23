from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.pigeons.models import Pigeon
from .models import PedigreeRecord
from .serializers import PedigreeSerializer

class PedigreeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pigeon_id):
        pigeon = get_object_or_404(Pigeon, pk=pigeon_id)
        try:
            record = pigeon.pedigree
            return Response(PedigreeSerializer(record).data)
        except PedigreeRecord.DoesNotExist:
            return Response({'detail': 'No pedigree found.'}, status=404)

class PedigreeEditView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pigeon_id):
        pigeon = get_object_or_404(Pigeon, pk=pigeon_id, owner=request.user)
        try:
            record = pigeon.pedigree
        except PedigreeRecord.DoesNotExist:
            record = None
        serializer = PedigreeSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(pigeon=pigeon)
        return Response(serializer.data)