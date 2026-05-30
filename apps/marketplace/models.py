from django.db import models
from django.conf import settings
from apps.pigeons.models import Pigeon

BD_DISTRICTS = [
    ('dhaka','Dhaka'), ('gazipur','Gazipur'), ('narayanganj','Narayanganj'),
    ('tangail','Tangail'), ('chittagong','Chittagong'), ('cox_bazar',"Cox's Bazar"),
    ('comilla','Comilla'), ('noakhali','Noakhali'), ('sylhet','Sylhet'),
    ('moulvibazar','Moulvibazar'), ('rajshahi','Rajshahi'), ('bogra','Bogra'),
    ('rangpur','Rangpur'), ('dinajpur','Dinajpur'), ('khulna','Khulna'),
    ('jessore','Jessore'), ('barisal','Barisal'), ('mymensingh','Mymensingh'),
    ('manikganj','Manikganj'), ('other','Other'),
]


class Listing(models.Model):
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('sold',     'Sold'),
        ('reserved', 'Reserved'),
        ('inactive', 'Inactive'),
    ]

    seller      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    pigeon      = models.OneToOneField(Pigeon, on_delete=models.CASCADE, related_name='listing')
    title       = models.CharField(max_length=200)
    description = models.TextField()
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    location    = models.CharField(max_length=100)
    district    = models.CharField(max_length=30, choices=BD_DISTRICTS, default='other')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_negotiable = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'listings'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        return self.status == 'active'

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class SavedListing(models.Model):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_listings')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_listings'
        unique_together = ('user', 'listing')


class Review(models.Model):
    reviewer   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    seller     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    listing    = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating     = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        unique_together = ('reviewer', 'seller')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reviewer} → {self.seller}: {self.rating}★'


class Offer(models.Model):
    STATUS = [
        ('pending',   'Pending'),
        ('accepted',  'Accepted'),
        ('rejected',  'Rejected'),
        ('countered', 'Countered'),
        ('withdrawn', 'Withdrawn'),
    ]

    listing        = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='offers')
    buyer          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_offers')
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    message        = models.TextField(blank=True)
    status         = models.CharField(max_length=15, choices=STATUS, default='pending')
    counter_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    counter_msg    = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'offers'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.buyer} offers BDT {self.amount} for {self.listing}'


class Payment(models.Model):
    METHOD = [('bkash', 'bKash'), ('nagad', 'Nagad'), ('rocket', 'Rocket')]
    STATUS = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('disputed', 'Disputed')]

    offer      = models.OneToOneField(Offer, on_delete=models.CASCADE, related_name='payment')
    buyer      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount     = models.DecimalField(max_digits=10, decimal_places=2)
    method     = models.CharField(max_length=10, choices=METHOD)
    trx_id     = models.CharField(max_length=100)
    status     = models.CharField(max_length=15, choices=STATUS, default='pending')
    note       = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
