from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

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