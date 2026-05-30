from django.db import models
from django.conf import settings
from apps.pigeons.models import Pigeon
from apps.compress import compress_image


class Contest(models.Model):
    title           = models.CharField(max_length=200)
    description     = models.TextField()
    start_date      = models.DateField()
    end_date        = models.DateField()
    voting_end_date = models.DateField()
    is_active       = models.BooleanField(default=True)
    winner          = models.OneToOneField('ContestEntry', null=True, blank=True, on_delete=models.SET_NULL, related_name='won_contest')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contests'
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class ContestEntry(models.Model):
    contest    = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='entries')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contest_entries')
    pigeon     = models.ForeignKey(Pigeon, null=True, blank=True, on_delete=models.SET_NULL, related_name='contest_entries')
    image      = models.ImageField(upload_to='contests/')
    caption    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contest_entries'
        unique_together = ('contest', 'user')

    def __str__(self):
        return f'{self.user} — {self.contest}'

    @property
    def vote_count(self):
        return self.votes.count()

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            compressed = compress_image(self.image, max_width=1200, quality=70)
            if compressed:
                self.image = compressed
        super().save(*args, **kwargs)


class ContestVote(models.Model):
    contest    = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name='votes')
    voter      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contest_votes')
    entry      = models.ForeignKey(ContestEntry, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contest_votes'
        unique_together = ('contest', 'voter')
