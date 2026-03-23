from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'full_name', 'location',
                     'is_verified', 'listing_count', 'avatar_preview', 'date_joined')
    list_filter   = ('is_verified', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'location')
    ordering      = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'avatar_preview', 'listing_count')

    fieldsets = (
        ('Account', {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone',
                       'location', 'bio', 'avatar', 'avatar_preview')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        ('Create User', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                       'first_name', 'last_name', 'location', 'is_verified')
        }),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;'
                'border-radius:50%;object-fit:cover;">',
                obj.avatar.url
            )
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;'
            'background:#2563eb;color:#fff;display:flex;align-items:center;'
            'justify-content:center;font-weight:bold;">{}</div>',
            obj.username[0].upper()
        )
    avatar_preview.short_description = 'Avatar'

    def listing_count(self, obj):
        count = obj.listings.filter(status='active').count()
        return format_html('<b style="color:#2563eb;">{}</b>', count)
    listing_count.short_description = 'Active Listings'

    actions = ['verify_users', 'unverify_users', 'deactivate_users']

    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} user(s) marked as verified.')
    verify_users.short_description = 'Mark selected users as verified'

    def unverify_users(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f'{updated} user(s) marked as unverified.')
    unverify_users.short_description = 'Mark selected users as unverified'

    def deactivate_users(self, request, queryset):
        updated = queryset.exclude(is_superuser=True).update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'