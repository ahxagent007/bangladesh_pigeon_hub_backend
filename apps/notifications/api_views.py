from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    actor_name   = serializers.CharField(source='actor.username', read_only=True, default=None)
    actor_avatar = serializers.SerializerMethodField()
    icon         = serializers.ReadOnlyField(source='type_icon')

    class Meta:
        model  = Notification
        fields = ('id', 'notif_type', 'icon', 'message', 'url',
                  'is_read', 'actor_name', 'actor_avatar', 'created_at')

    def get_actor_avatar(self, obj):
        req = self.context.get('request')
        if obj.actor and obj.actor.avatar:
            url = obj.actor.avatar.url
            if req and not url.startswith('http'):
                return req.build_absolute_uri(url)
            return url
        return None


class NotificationListView(generics.ListAPIView):
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor').order_by('-created_at')[:50]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # Mark all as read after fetching
        Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return response


class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({'count': count})
