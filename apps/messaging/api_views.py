from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class StartConversationView(APIView):
    """POST /api/messages/start/  body: {"listing_id": N}
    Finds or creates a conversation between the current user and a listing's
    seller, then returns the conversation id (so the app can open it)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from apps.marketplace.models import Listing
        listing_id = request.data.get('listing_id')
        if not listing_id:
            return Response({'error': 'listing_id is required.'}, status=400)

        listing = get_object_or_404(Listing, pk=listing_id)
        if listing.seller == request.user:
            return Response({'error': "You can't message your own listing."}, status=400)

        existing = (Conversation.objects
                    .filter(participants=request.user, listing=listing)
                    .filter(participants=listing.seller)
                    .first())
        if existing:
            return Response({'id': existing.id, 'created': False})

        conv = Conversation.objects.create(listing=listing)
        conv.participants.add(request.user, listing.seller)
        return Response({'id': conv.id, 'created': True}, status=status.HTTP_201_CREATED)


class ConversationListView(generics.ListAPIView):
    serializer_class   = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.conversations.order_by('-updated_at')

    def get_serializer_context(self):
        return {'request': self.request}

class ConversationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        conv = get_object_or_404(
            Conversation.objects.prefetch_related('messages__sender'),
            pk=pk, participants=request.user
        )
        conv.messages.exclude(sender=request.user).update(is_read=True)
        messages = MessageSerializer(
            conv.messages.order_by('created_at'), many=True
        ).data
        return Response({'id': conv.id, 'messages': messages})

class SendMessageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk, participants=request.user)
        body = request.data.get('body', '').strip()
        if not body:
            return Response({'error': 'Message cannot be empty.'}, status=400)
        msg = Message.objects.create(
            conversation=conv, sender=request.user, body=body
        )
        conv.save()
        return Response(MessageSerializer(msg).data, status=201)