from django.db import models
from autoslug import AutoSlugField
from django.contrib.auth.models import AbstractUser
# Create your models here.)


class User(AbstractUser):
    job_title = models.CharField(max_length=250, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=11, unique=True, blank=True)




class Post(models.Model):

    class PostStatus(models.TextChoices):
        PUBLIC = 'PB', 'Public'
        PRIVATE = 'PV', 'Private'

    title = models.CharField(max_length=250)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=PostStatus.choices, default=PostStatus.PUBLIC)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    slug = AutoSlugField(populate_from='title', unique=True)
    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True)


