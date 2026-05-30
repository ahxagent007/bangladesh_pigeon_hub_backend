from django.contrib import admin
from .models import Post, PostImage, Like, Comment

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'like_count', 'comment_count', 'created_at')
    list_filter  = ('created_at',)
    inlines      = [PostImageInline]

    def content_preview(self, obj):
        return obj.content[:60]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content', 'created_at')
