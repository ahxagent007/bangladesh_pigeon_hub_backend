from django.db import models
from django.conf import settings
from apps.pigeons.models import Pigeon
from apps.compress import compress_image


class Post(models.Model):
    author  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wall_posts')
    pigeon  = models.ForeignKey(Pigeon, on_delete=models.SET_NULL, null=True, blank=True, related_name='wall_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wall_posts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:60]}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class PostImage(models.Model):
    post  = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='wall/')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'wall_post_images'
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.image and not self.image._committed:
            compressed = compress_image(self.image, max_width=1200, quality=65)
            if compressed:
                self.image = compressed
        super().save(*args, **kwargs)


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wall_likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wall_likes'
        unique_together = ('user', 'post')


class Comment(models.Model):
    author  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wall_comments')
    post    = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wall_comments'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:60]}"
