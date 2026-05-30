from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import F
from apps.pigeons.models import Pigeon
from apps.compress import compress_image


class Auction(models.Model):
    STATUS = [
        ('upcoming', 'Upcoming'),
        ('live',     'Live'),
        ('ended',    'Ended'),
        ('cancelled','Cancelled'),
    ]

    seller          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auctions')
    pigeon          = models.ForeignKey(Pigeon, on_delete=models.SET_NULL, null=True, blank=True, related_name='auctions')
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    image           = models.ImageField(upload_to='auctions/', null=True, blank=True)
    pedigree_image  = models.ImageField(upload_to='auction_pedigree/', null=True, blank=True,
                                        help_text='Pedigree certificate or family tree photo')
    starting_price  = models.DecimalField(max_digits=10, decimal_places=2)
    reserve_price   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          help_text='Hidden minimum price to win. Leave blank for no reserve.')
    min_increment   = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('50'),
                                          help_text='Minimum raise per bid (BDT)')
    current_price   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    bid_count       = models.PositiveIntegerField(default=0)
    views_count     = models.PositiveIntegerField(default=0)
    start_time      = models.DateTimeField()
    end_time        = models.DateTimeField()
    anti_snipe_min  = models.PositiveSmallIntegerField(default=2,
                                                       help_text='Extend by this many minutes if bid placed near end')
    status          = models.CharField(max_length=12, choices=STATUS, default='upcoming')
    winner          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='won_auctions')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auctions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    # ── Computed helpers ────────────────────────────────────────────────────

    @property
    def display_price(self):
        return self.current_price if self.current_price else self.starting_price

    @property
    def min_next_bid(self):
        return self.display_price + self.min_increment

    @property
    def time_remaining(self):
        if self.status in ('ended', 'cancelled'):
            return None
        delta = self.end_time - timezone.now()
        return delta if delta.total_seconds() > 0 else None

    @property
    def seconds_remaining(self):
        tr = self.time_remaining
        return int(tr.total_seconds()) if tr else 0

    @property
    def reserve_met(self):
        if self.reserve_price is None:
            return True
        return bool(self.current_price and self.current_price >= self.reserve_price)

    def get_cover_image(self):
        """Main display image: auction cover > first gallery > pigeon primary."""
        if self.image:
            return self.image.url
        first_gallery = self.gallery.first()
        if first_gallery:
            return first_gallery.image.url
        if self.pigeon:
            img = self.pigeon.primary_image
            if img:
                return img.image.url
        return None

    def get_all_gallery_images(self):
        """
        All images to show in the detail-page gallery, in display order:
        cover image first, then AuctionImage rows, then pigeon images as fallback.
        Returns a list of dicts: {'url': ..., 'caption': ...}
        """
        imgs = []
        if self.image:
            imgs.append({'url': self.image.url, 'caption': 'Main photo'})
        for ai in self.gallery.all():
            imgs.append({'url': ai.image.url, 'caption': ai.caption or ''})
        if not imgs and self.pigeon:
            for pi in self.pigeon.images.all():
                imgs.append({'url': pi.image.url, 'caption': pi.caption or ''})
        return imgs

    # ── State transitions ────────────────────────────────────────────────────

    def sync_status(self):
        """Call at request time to auto-activate or auto-finalize."""
        now = timezone.now()
        changed = False
        if self.status == 'upcoming' and now >= self.start_time:
            self.status = 'live'
            changed = True
        if self.status == 'live' and now > self.end_time:
            self._finalize()
            return  # finalize calls save
        if changed:
            self.save(update_fields=['status'])

    def _finalize(self):
        """Determine winner, transfer pigeon ownership, fire notifications."""
        from apps.notifications.models import notify
        top_bid = self.bids.order_by('-amount').first()
        if top_bid and (self.reserve_price is None or top_bid.amount >= self.reserve_price):
            self.winner = top_bid.bidder
            if self.pigeon:
                self.pigeon.owner    = top_bid.bidder
                self.pigeon.is_for_sale = False
                self.pigeon.save()
                try:
                    self.pigeon.listing.status = 'sold'
                    self.pigeon.listing.save()
                except Exception:
                    pass
            notify(
                top_bid.bidder, self.seller, 'offer_accepted',
                f'🎉 You won the auction "{self.title}" with BDT {top_bid.amount}!',
                f'/auctions/{self.pk}/',
            )
            notify(
                self.seller, top_bid.bidder, 'payment',
                f'Auction "{self.title}" ended. Winner: {top_bid.bidder.username} (BDT {top_bid.amount}).',
                f'/auctions/{self.pk}/dashboard/',
            )
        self.status = 'ended'
        self.save(update_fields=['status', 'winner'])

    def increment_views(self):
        Auction.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            compressed = compress_image(self.image, max_width=1200, quality=70)
            if compressed:
                self.image = compressed
        if self.pedigree_image and not self.pedigree_image._committed:
            compressed = compress_image(self.pedigree_image, max_width=1600, quality=72)
            if compressed:
                self.pedigree_image = compressed
        super().save(*args, **kwargs)


class Bid(models.Model):
    auction    = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bids')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auction_bids'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.bidder} → BDT {self.amount} on {self.auction}'


class AuctionImage(models.Model):
    """Additional gallery images for an auction listing."""
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='gallery')
    image   = models.ImageField(upload_to='auctions/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'auction_images'
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            compressed = compress_image(self.image, max_width=1200, quality=65)
            if compressed:
                self.image = compressed
        super().save(*args, **kwargs)


class AuctionWatch(models.Model):
    auction    = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='watchers')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watched_auctions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auction_watches'
        unique_together = ('auction', 'user')
