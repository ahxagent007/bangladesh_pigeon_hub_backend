from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.compress import compress_image

class User(AbstractUser):
    """Extended user model for pigeon platform."""
    phone       = models.CharField(max_length=20, blank=True, null=True)
    location    = models.CharField(max_length=100, blank=True)
    bio         = models.TextField(blank=True)
    avatar      = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    language    = models.CharField(max_length=5, choices=[('en','English'),('bn','বাংলা')], default='en')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if self.avatar and not self.avatar._committed:
            compressed = compress_image(self.avatar, max_width=400, quality=60)
            if compressed:
                self.avatar = compressed
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def listing_count(self):
        return self.listings.filter(is_active=True).count()

    @property
    def avg_rating(self):
        reviews = self.received_reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()


class Follow(models.Model):
    follower   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'follows'
        unique_together = ('follower', 'following')