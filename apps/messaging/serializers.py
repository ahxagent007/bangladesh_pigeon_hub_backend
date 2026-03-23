from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    class Meta:
        model = Message
        fields = ('id', 'body', 'sender', 'sender_name', 'is_read', 'created_at')
        read_only_fields = ('sender', 'created_at', 'is_read')

class ConversationSerializer(serializers.ModelSerializer):
    last_message = MessageSerializer(read_only=True)
    other_user   = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id', 'other_user', 'last_message', 'updated_at')

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request:
            other = obj.get_other_participant(request.user)
            if other:
                return {'id': other.id, 'username': other.username}
        return None