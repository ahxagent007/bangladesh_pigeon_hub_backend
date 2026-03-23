from django.contrib import admin
from django.utils.html import format_html
from .models import Breed, Pigeon, PigeonImage


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    list_display  = ('name', 'origin', 'pigeon_count', 'created_at')
    search_fields = ('name', 'origin')
    ordering      = ('name',)
    readonly_fields = ('created_at',)

    def pigeon_count(self, obj):
        return obj.pigeons.count()
    pigeon_count.short_description = 'Total Pigeons'


class PigeonImageInline(admin.TabularInline):
    model   = PigeonImage
    extra   = 1
    fields  = ('image', 'is_primary', 'caption', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:60px;'
                'object-fit:cover;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'


@admin.register(Pigeon)
class PigeonAdmin(admin.ModelAdmin):
    list_display  = ('name', 'ring_number', 'owner_link', 'breed',
                     'gender', 'color', 'age_display',
                     'is_for_sale', 'primary_image_preview', 'created_at')
    list_filter   = ('gender', 'color', 'breed', 'is_for_sale', 'created_at')
    search_fields = ('name', 'ring_number', 'owner__username',
                     'breed__name', 'description')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'age_display', 'primary_image_preview')
    inlines       = [PigeonImageInline]
    list_per_page = 25

    fieldsets = (
        ('Basic Info', {
            'fields': ('owner', 'name', 'ring_number', 'breed')
        }),
        ('Physical Details', {
            'fields': ('gender', 'color', 'date_of_birth',
                       'age_display', 'weight')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Status', {
            'fields': ('is_for_sale',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def owner_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.owner.pk, obj.owner.username
        )
    owner_link.short_description = 'Owner'

    def primary_image_preview(self, obj):
        img = obj.primary_image
        if img:
            return format_html(
                '<img src="{}" style="width:60px;height:50px;'
                'object-fit:cover;border-radius:4px;">',
                img.image.url
            )
        return '🐦'
    primary_image_preview.short_description = 'Photo'

    actions = ['mark_for_sale', 'mark_not_for_sale']

    def mark_for_sale(self, request, queryset):
        updated = queryset.update(is_for_sale=True)
        self.message_user(request, f'{updated} pigeon(s) marked for sale.')
    mark_for_sale.short_description = 'Mark selected pigeons as for sale'

    def mark_not_for_sale(self, request, queryset):
        updated = queryset.update(is_for_sale=False)
        self.message_user(request, f'{updated} pigeon(s) marked as not for sale.')
    mark_not_for_sale.short_description = 'Remove from sale'


@admin.register(PigeonImage)
class PigeonImageAdmin(admin.ModelAdmin):
    list_display  = ('pigeon', 'is_primary', 'caption', 'image_preview', 'uploaded_at')
    list_filter   = ('is_primary',)
    search_fields = ('pigeon__name', 'caption')
    readonly_fields = ('uploaded_at', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:100px;height:75px;'
                'object-fit:cover;border-radius:4px;">',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Preview'