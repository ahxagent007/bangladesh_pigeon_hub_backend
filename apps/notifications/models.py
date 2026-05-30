from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPES = [
        ('like',             '❤️ Post Liked'),
        ('comment',          '💬 Comment'),
        ('follow',           '👤 New Follower'),
        ('offer_received',   '💰 Offer Received'),
        ('offer_accepted',   '✅ Offer Accepted'),
        ('offer_rejected',   '❌ Offer Declined'),
        ('offer_countered',  '🔄 Offer Countered'),
        ('review',           '⭐ New Review'),
        ('message',          '✉️ New Message'),
        ('payment',          '💳 Payment Update'),
        ('contest_winner',   '🏆 Contest Winner'),
    ]

    recipient  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notif_type = models.CharField(max_length=30, choices=TYPES)
    message    = models.CharField(max_length=300)
    url        = models.CharField(max_length=300, blank=True)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    _ICONS = {
        'like': '❤️', 'comment': '💬', 'follow': '👤',
        'offer_received': '💰', 'offer_accepted': '✅',
        'offer_rejected': '❌', 'offer_countered': '🔄',
        'review': '⭐', 'message': '✉️',
        'payment': '💳', 'contest_winner': '🏆',
    }

    @property
    def type_icon(self):
        return self._ICONS.get(self.notif_type, '🔔')

    def __str__(self):
        return f'→ {self.recipient}: {self.message[:60]}'


def notify(recipient, actor, notif_type, message, url=''):
    """Convenience helper — call from any view to create a notification."""
    if recipient == actor:
        return
    Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notif_type=notif_type,
        message=message,
        url=url,
    )
