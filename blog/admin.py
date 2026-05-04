from django.contrib import admin
from .models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()


# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created', 'status', 'slug']
    list_editable = ['status']
    # readonly_fields = ['slug']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'is_staff']
    list_editable = ['is_staff']
    list_display_links = ['username']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'created', 'is_active']
    list_editable = ['is_active']