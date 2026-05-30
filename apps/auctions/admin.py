from django.contrib import admin
from .models import Auction, Bid, AuctionWatch


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ('bidder', 'amount', 'created_at')


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display  = ('title', 'seller', 'status', 'display_price', 'bid_count', 'start_time', 'end_time')
    list_filter   = ('status',)
    search_fields = ('title', 'seller__username')
    inlines       = [BidInline]
    readonly_fields = ('bid_count', 'views_count', 'current_price', 'winner')
    actions       = ['force_finalize']

    def force_finalize(self, request, queryset):
        for auction in queryset.filter(status='live'):
            auction._finalize()
        self.message_user(request, 'Selected auctions finalized.')
    force_finalize.short_description = 'Force finalize selected auctions'


admin.site.register(Bid)
admin.site.register(AuctionWatch)
