from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
from core.settings import AUTH_USER_MODEL
from django.utils.text import slugify
# Create your models here.)


class User(AbstractUser):
    job_title = models.CharField(max_length=250, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=11, unique=True, blank=True, null=True)


class Post(models.Model):

    class PostStatus(models.TextChoices):
        PUBLIC = 'PB', 'Public'
        PRIVATE = 'PV', 'Private'

    title = models.CharField(max_length=250, unique=True)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2, choices=PostStatus.choices, default=PostStatus.PUBLIC)
    author = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(
        AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    slug = AutoSlugField(populate_from='title', unique=True, always_update=True)
    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author'])
        ]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='replies', blank=True, null=True)

    def __str__(self):
        return f'by {self.user.username} on post: {self.post.title}'

    class Meta:
        indexes = [
            models.Index(fields=['post', 'is_active']),
            models.Index(fields=['post', 'created']),

            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'created']),
        ]
