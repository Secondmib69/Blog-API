from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')


app_name = 'blog'

urlpatterns = [
    path('', include(router.urls)),
    path('posts/', PostListAPIView.as_view(), name='post-list'),
    path('posts/<slug>/', PostDetailAPIView.as_view(), name='post-detail'), 
    path('posts/<slug>/like/', ToggleLikeAPIView.as_view(), name='like-post'),
    path('posts/<slug>/comments/', PostCommentListAPIView.as_view(), name='comment-list'),
    path('posts/<slug>/comments/<id>/', PostCommentDetailAPIView.as_view(), name='comment-detail')
]