from django.contrib import admin
from .models import RemoteConfig


@admin.register(RemoteConfig)
class RemoteConfigAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'cam', 'updated_at')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Feature Flags', {
            'fields': ('cam',),
            'description': (
                'These flags are read by the external company app via '
                '<code>GET /app/track</code>. Changes take effect immediately.'
            ),
        }),
        ('Meta', {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        # Only one row may ever exist
        return not RemoteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
