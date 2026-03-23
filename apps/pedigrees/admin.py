from django.contrib import admin
from django.utils.html import format_html
from .models import PedigreeRecord


@admin.register(PedigreeRecord)
class PedigreeRecordAdmin(admin.ModelAdmin):
    list_display  = ('pigeon_link', 'sire_link', 'dam_link',
                     'is_public', 'has_notes', 'created_at')
    list_filter   = ('is_public', 'created_at')
    search_fields = ('pigeon__name', 'pigeon__ring_number',
                     'sire__name', 'dam__name')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'pedigree_summary')

    fieldsets = (
        ('Subject', {
            'fields': ('pigeon',)
        }),
        ('Parents', {
            'fields': ('sire', 'dam')
        }),
        ('Details', {
            'fields': ('notes', 'is_public')
        }),
        ('Pedigree Summary', {
            'fields': ('pedigree_summary',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def pigeon_link(self, obj):
        return format_html(
            '<a href="/admin/pigeons/pigeon/{}/change/"><b>{}</b></a>',
            obj.pigeon.pk, obj.pigeon.name
        )
    pigeon_link.short_description = 'Pigeon'

    def sire_link(self, obj):
        if obj.sire:
            return format_html(
                '<a href="/admin/pigeons/pigeon/{}/change/">'
                '♂ {}</a>',
                obj.sire.pk, obj.sire.name
            )
        return format_html('<span style="color:#9ca3af;">Unknown</span>')
    sire_link.short_description = 'Sire (Father)'

    def dam_link(self, obj):
        if obj.dam:
            return format_html(
                '<a href="/admin/pigeons/pigeon/{}/change/">'
                '♀ {}</a>',
                obj.dam.pk, obj.dam.name
            )
        return format_html('<span style="color:#9ca3af;">Unknown</span>')
    dam_link.short_description = 'Dam (Mother)'

    def has_notes(self, obj):
        if obj.notes:
            return format_html(
                '<span style="color:#16a34a;font-weight:600;">Yes</span>'
            )
        return format_html('<span style="color:#9ca3af;">No</span>')
    has_notes.short_description = 'Notes'

    def pedigree_summary(self, obj):
        lines = [
            f'<b>{obj.pigeon.name}</b>',
        ]
        if obj.sire:
            lines.append(f'&nbsp;&nbsp;├─ Sire: <b>{obj.sire.name}</b>'
                         f' ({obj.sire.breed or "Unknown breed"})')
            try:
                gs = obj.sire.pedigree
                if gs.sire:
                    lines.append(f'&nbsp;&nbsp;│&nbsp;&nbsp;├─ {gs.sire.name}')
                if gs.dam:
                    lines.append(f'&nbsp;&nbsp;│&nbsp;&nbsp;└─ {gs.dam.name}')
            except Exception:
                pass
        if obj.dam:
            lines.append(f'&nbsp;&nbsp;└─ Dam: <b>{obj.dam.name}</b>'
                         f' ({obj.dam.breed or "Unknown breed"})')
            try:
                gd = obj.dam.pedigree
                if gd.sire:
                    lines.append(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├─ {gd.sire.name}')
                if gd.dam:
                    lines.append(f'&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└─ {gd.dam.name}')
            except Exception:
                pass
        return format_html(
            '<pre style="font-family:monospace;font-size:13px;'
            'background:#f9fafb;padding:12px;border-radius:6px;'
            'border:1px solid #e5e7eb;">{}</pre>',
            format_html('<br>'.join(lines))
        )
    pedigree_summary.short_description = 'Tree Preview'

    actions = ['make_public', 'make_private']

    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} pedigree(s) set to public.')
    make_public.short_description = 'Make selected pedigrees public'

    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} pedigree(s) set to private.')
    make_private.short_description = 'Make selected pedigrees private'