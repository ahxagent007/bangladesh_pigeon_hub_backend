from django.contrib import admin
from django.utils.html import format_html
from .models import Listing, SavedListing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'seller_link', 'pigeon_link', 'price_display',
                     'location', 'status_badge', 'is_negotiable',
                     'views_count', 'created_at')
    list_filter   = ('status', 'is_negotiable', 'created_at',
                     'pigeon__breed')
    search_fields = ('title', 'seller__username', 'pigeon__name',
                     'location', 'description')
    ordering      = ('-created_at',)
    readonly_fields = ('views_count', 'created_at', 'updated_at',
                       'pigeon_image_preview')
    list_per_page = 25

    fieldsets = (
        ('Listing Info', {
            'fields': ('seller', 'pigeon', 'pigeon_image_preview',
                       'title', 'description')
        }),
        ('Pricing & Location', {
            'fields': ('price', 'is_negotiable', 'location')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Stats', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def seller_link(self, obj):
        return format_html(
            '<a href="/admin/users/user/{}/change/">{}</a>',
            obj.seller.pk, obj.seller.username
        )
    seller_link.short_description = 'Seller'

    def pigeon_link(self, obj):
        return format_html(
            '<a href="/admin/pigeons/pigeon/{}/change/">{}</a>',
            obj.pigeon.pk, obj.pigeon.name
        )
    pigeon_link.short_description = 'Pigeon'

    def price_display(self, obj):
        return format_html('<b>BDT{}</b>', obj.price)
    price_display.short_description = 'Price'

    def status_badge(self, obj):
        colors = {
            'active':   '#16a34a',
            'sold':     '#dc2626',
            'reserved': '#d97706',
            'inactive': '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;'
            'border-radius:999px;font-size:12px;font-weight:600;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def pigeon_image_preview(self, obj):
        img = obj.pigeon.primary_image
        if img:
            return format_html(
                '<img src="{}" style="width:120px;height:90px;'
                'object-fit:cover;border-radius:6px;">',
                img.image.url
            )
        return '—'
    pigeon_image_preview.short_description = 'Pigeon Photo'

    actions = ['mark_active', 'mark_sold', 'mark_inactive']

    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} listing(s) set to active.')
    mark_active.short_description = 'Set selected listings to Active'

    def mark_sold(self, request, queryset):
        updated = queryset.update(status='sold')
        self.message_user(request, f'{updated} listing(s) marked as sold.')
    mark_sold.short_description = 'Mark selected listings as Sold'

    def mark_inactive(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} listing(s) set to inactive.')
    mark_inactive.short_description = 'Set selected listings to Inactive'


@admin.register(SavedListing)
class SavedListingAdmin(admin.ModelAdmin):
    list_display  = ('user', 'listing_title', 'listing_price', 'saved_at')
    search_fields = ('user__username', 'listing__title')
    ordering      = ('-saved_at',)
    readonly_fields = ('saved_at',)

    def listing_title(self, obj):
        return obj.listing.title
    listing_title.short_description = 'Listing'

    def listing_price(self, obj):
        return format_html('<b>BDT{}</b>', obj.listing.price)
    listing_price.short_description = 'Price'