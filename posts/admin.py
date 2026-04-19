from django.contrib import admin
from .models import Post, Like, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'privacy', 'created_at']
    list_filter = ['privacy']
    search_fields = ['author__username', 'content']

admin.site.register(Comment)
admin.site.register(Like)
