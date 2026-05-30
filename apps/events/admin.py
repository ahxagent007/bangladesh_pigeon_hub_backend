from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'district', 'date', 'organizer')
    list_filter  = ('event_type', 'district')
