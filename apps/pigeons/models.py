from django.db import models
from django.conf import settings

class Breed(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    origin = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'breeds'
        ordering = ['name']

    def __str__(self):
        return self.name


class Pigeon(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')]
    COLOR_CHOICES = [
        ('blue', 'Blue'), ('red', 'Red'), ('white', 'White'),
        ('black', 'Black'), ('silver', 'Silver'), ('other', 'Other'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pigeons'
    )
    breed = models.ForeignKey(
        Breed, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='pigeons'
    )
    name = models.CharField(max_length=100)
    ring_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='blue')
    date_of_birth = models.DateField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True, help_text='Weight in grams')
    description = models.TextField(blank=True)
    is_for_sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pigeons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.ring_number or 'No Ring'})"

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first()
        return img or self.images.first()

    @property
    def age_display(self):
        if not self.date_of_birth:
            return 'Unknown'
        from datetime import date
        delta = date.today() - self.date_of_birth
        years = delta.days // 365
        months = (delta.days % 365) // 30
        if years > 0:
            return f"{years}y {months}m"
        return f"{months} months"


class PigeonImage(models.Model):
    pigeon = models.ForeignKey(
        Pigeon, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='pigeons/')
    is_primary = models.BooleanField(default=False)
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pigeon_images'

    def save(self, *args, **kwargs):
        # Ensure only one primary image per pigeon
        if self.is_primary:
            PigeonImage.objects.filter(
                pigeon=self.pigeon, is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)