from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .logic import generate_feed, PURPOSE_TARGETS

class FeedGenerateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        purpose        = request.query_params.get('purpose', 'maintenance')
        target_protein = request.query_params.get('target_protein')
        if purpose not in PURPOSE_TARGETS:
            return Response({'error': 'Invalid purpose.'}, status=400)
        result = generate_feed(purpose, target_protein)
        return Response(result)