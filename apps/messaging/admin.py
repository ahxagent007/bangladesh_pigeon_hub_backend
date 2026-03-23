from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model         = Message
    extra         = 0
    fields        = ('sender', 'body_preview', 'is_read', 'created_at')
    readonly_fields = ('sender', 'body_preview', 'is_read', 'created_at')
    can_delete    = False
    max_num       = 0
    ordering      = ('created_at',)

    def body_preview(self, obj):
        return obj.body[:80] + '…' if len(obj.body) > 80 else obj.body
    body_preview.short_description = 'Message'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display  = ('id', 'participants_display', 'listing_link',
                     'message_count', 'last_message_preview', 'updated_at')
    list_filter   = ('created_at', 'updated_at')
    search_fields = ('participants__username', 'listing__title',
                     'messages__body')
    ordering      = ('-updated_at',)
    readonly_fields = ('created_at', 'updated_at', 'participants_display',
                       'full_chat_log')
    inlines       = [MessageInline]

    fieldsets = (
        ('Conversation', {
            'fields': ('participants', 'listing', 'participants_display')
        }),
        ('Chat Log', {
            'fields': ('full_chat_log',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def participants_display(self, obj):
        users = obj.participants.all()
        links = ' &nbsp;↔&nbsp; '.join(
            f'<a href="/admin/users/user/{u.pk}/change/"><b>{u.username}</b></a>'
            for u in users
        )
        return format_html(links)
    participants_display.short_description = 'Participants'

    def listing_link(self, obj):
        if obj.listing:
            return format_html(
                '<a href="/admin/marketplace/listing/{}/change/">{}</a>',
                obj.listing.pk,
                obj.listing.title[:40]
            )
        return format_html('<span style="color:#9ca3af;">—</span>')
    listing_link.short_description = 'About Listing'

    def message_count(self, obj):
        count   = obj.messages.count()
        unread  = obj.messages.filter(is_read=False).count()
        if unread:
            return format_html(
                '{} <span style="background:#ef4444;color:#fff;'
                'padding:1px 6px;border-radius:999px;font-size:11px;">'
                '{} unread</span>',
                count, unread
            )
        return count
    message_count.short_description = 'Messages'

    def last_message_preview(self, obj):
        last = obj.last_message
        if last:
            preview = last.body[:50] + '…' if len(last.body) > 50 else last.body
            return format_html(
                '<span style="color:#6b7280;font-size:13px;">'
                '<b>{}</b>: {}</span>',
                last.sender.username, preview
            )
        return '—'
    last_message_preview.short_description = 'Last Message'

    def full_chat_log(self, obj):
        messages = obj.messages.order_by('created_at').select_related('sender')
        if not messages:
            return 'No messages yet.'
        rows = []
        for msg in messages:
            read_icon = '✓✓' if msg.is_read else '✓'
            read_color = '#2563eb' if msg.is_read else '#9ca3af'
            rows.append(
                f'<div style="margin-bottom:8px;padding:8px 12px;'
                f'background:#f9fafb;border-radius:8px;border-left:'
                f'3px solid #2563eb;">'
                f'<div style="font-size:12px;color:#6b7280;margin-bottom:4px;">'
                f'<b>{msg.sender.username}</b> · '
                f'{msg.created_at.strftime("%d %b %Y %H:%M")} '
                f'<span style="color:{read_color};">{read_icon}</span>'
                f'</div>'
                f'<div style="font-size:14px;">{msg.body}</div>'
                f'</div>'
            )
        return format_html(
            '<div style="max-height:400px;overflow-y:auto;'
            'padding:8px;background:#fff;border:1px solid #e5e7eb;'
            'border-radius:8px;">{}</div>',
            format_html(''.join(rows))
        )
    full_chat_log.short_description = 'Chat Log'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('sender_link', 'conversation_link', 'body_preview',
                     'is_read', 'created_at')
    list_filter   = ('is_read', 'created_at')
    search_fields = ('sender__username', 'body',
                     'conversation__participants__username')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)
    list_per_page = 50

    def sender_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.sender.pk, obj.sender.username
        )
    sender_link.short_description = 'Sender'

    def conversation_link(self, obj):
        return format_html(
            '<a href="/admin/messaging/conversation/{}/change/">'
            'Conversation #{}</a>',
            obj.conversation.pk, obj.conversation.pk
        )
    conversation_link.short_description = 'Conversation'

    def body_preview(self, obj):
        return obj.body[:80] + '…' if len(obj.body) > 80 else obj.body
    body_preview.short_description = 'Message'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} message(s) marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'