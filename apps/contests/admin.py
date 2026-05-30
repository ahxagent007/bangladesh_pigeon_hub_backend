from django.contrib import admin
from .models import Contest, ContestEntry, ContestVote

@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'voting_end_date', 'is_active')
    list_editable = ('is_active',)

admin.site.register(ContestEntry)
admin.site.register(ContestVote)
