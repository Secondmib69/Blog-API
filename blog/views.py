from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from rest_framework import generics, exceptions, status
from .serializers import PostSerializer, PostCommentSerializer, CommentApproveSerializer, User, UserSerializer
from django.db.models import Q
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsPostAuthorOrStaffDeleteOrReadOnly, IsStaffOrCommentUserDelete, UserRolePermission
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets
# Create your views here.



class PostListAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTCookieAuthentication]
    filter_backends  = [OrderingFilter]
    ordering_fields = ['created', 'updated']
    # ordering = ['-created']


    def get_queryset(self):
        qs = Post.objects.all()
        if self.request.user.is_anonymous:
            return qs.filter(status='PB')
        elif not self.request.user.is_staff:
            return qs.filter(Q(status='PB') | Q(status='PV', author=self.request.user))
        return qs

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    lookup_field= 'slug'
    permission_classes = [IsPostAuthorOrStaffDeleteOrReadOnly]
    authentication_classes = [JWTCookieAuthentication]

    def get_queryset(self):
        qs = Post.objects.all()
        if self.request.user.is_anonymous:
            return qs.filter(status='PB')
        elif not self.request and self.request.user.is_staff:
            return qs.filter(Q(status='PB') | Q(status='PV', author=self.request.user))
        return qs


class PostCommentListAPIView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTCookieAuthentication]


    def get_queryset(self):
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
        qs = Comment.objects.filter(post=post)
        if not self.request.user.is_staff:
            return qs.filter(is_active=True)
        return qs
    
    def perform_create(self, serializer):
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
        if self.request.user.is_authenticated:
            serializer.save(post=post, user=self.request.user)

    # def get_serializer_context(self): # we pass context to the serializer and then use the context
    #     context = super().get_serializer_context()
    #     post = get_object_or_404(Post, slug=self.kwargs.get('slug')) 
    #     context['post'] = post
    #     return context
    
class PostCommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    # serializer_class = PostCommentSerializer
    permission_classes = [IsStaffOrCommentUserDelete]
    authentication_classes = [JWTCookieAuthentication]
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
        qs = Comment.objects.filter(post=post)
        if not self.request.user.is_staff:
            return qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.request.user.is_staff and self.request.method in ('PUT', 'PATCH'):
            return CommentApproveSerializer
        return PostCommentSerializer
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [UserRolePermission]

    def get_serializer_class(self):
        # if self.action in ['create', 'retrieve', 'list']:
        return UserSerializer
            
    
    # def get_permissions(self):
    #     if self.action == 'create':
    #         if not self.request.user.is_superuser:
    #             raise PermissionDenied
    #     return super().get_permissions()