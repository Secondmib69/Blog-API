from django.urls import path, include
from .views import *


app_name = 'blog'

urlpatterns = [
    path('posts/', PostListAPIView.as_view(), name='post_list'),
    path('posts/<slug>/', PostDetailAPIView.as_view(), name='post-detail'), 
    path('posts/<slug>/comments/', PostCommentListAPIView.as_view(), name='comment-list'),
    path('posts/<slug>/comments/<id>/', PostCommentDetailAPIView.as_view(), name='comment-detail')
]