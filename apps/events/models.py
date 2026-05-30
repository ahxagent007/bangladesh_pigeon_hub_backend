from django.db import models
from django.conf import settings
from apps.compress import compress_image

BD_DISTRICTS = [
    ('dhaka','Dhaka'), ('gazipur','Gazipur'), ('narayanganj','Narayanganj'),
    ('tangail','Tangail'), ('chittagong','Chittagong'), ('cox_bazar',"Cox's Bazar"),
    ('comilla','Comilla'), ('noakhali','Noakhali'), ('sylhet','Sylhet'),
    ('moulvibazar','Moulvibazar'), ('rajshahi','Rajshahi'), ('bogra','Bogra'),
    ('rangpur','Rangpur'), ('dinajpur','Dinajpur'), ('khulna','Khulna'),
    ('jessore','Jessore'), ('barisal','Barisal'), ('mymensingh','Mymensingh'),
    ('manikganj','Manikganj'), ('other','Other'),
]

class Event(models.Model):
    TYPES = [
        ('show',    'Pigeon Show'),
        ('race',    'Race'),
        ('auction', 'Auction'),
        ('meetup',  'Enthusiast Meetup'),
        ('other',   'Other'),
    ]

    organizer   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_events')
    title       = models.CharField(max_length=200)
    description = models.TextField()
    event_type  = models.CharField(max_length=20, choices=TYPES, default='show')
    location    = models.CharField(max_length=200)
    district    = models.CharField(max_length=30, choices=BD_DISTRICTS, default='other')
    date        = models.DateField()
    time        = models.TimeField(null=True, blank=True)
    image       = models.ImageField(upload_to='events/', null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'events'
        ordering = ['date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            compressed = compress_image(self.image, max_width=1200, quality=70)
            if compressed:
                self.image = compressed
        super().save(*args, **kwargs)
