from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from rest_framework import generics, exceptions, status, views
from .serializers import PostSerializer, PostCommentSerializer, CommentApproveSerializer, User, UserCreateSerializer, UserSerializer
from django.db.models import Q, Count
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import IsPostAuthorOrStaffDeleteOrReadOnly, IsStaffOrCommentUserDelete, UserRolePermission
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import FilterSet, DjangoFilterBackend
from .filters import RoleFilter, RoleSearchFilter
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, Response
from rest_framework import viewsets
# Create your views here.
        

class PostListAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTCookieAuthentication]
    filter_backends  = [SearchFilter, RoleFilter, OrderingFilter]
    search_fields = ['title', 'content', 'author__username']
    ordering_fields = ['created', 'updated', 'likes_count']
    ordering = ['-created']
    pagination_class = PageNumberPagination


    class StaffFilterSet(FilterSet):
        class Meta:
            model = Post
            fields = ['status']


    def get_queryset(self):
        qs = Post.objects.annotate(likes_count=Count('likes'))
        user_id = self.request.query_params.get('user_id')
        user = self.request.user
        if user.is_anonymous:
            if user_id:
                return qs.filter(author__id=user_id, status='PB')
            return qs.filter(status='PB')


        if not user.is_staff:
            if user_id:
                if user_id == str(user.id): # query params are string in orm no need to transform but in python its needed
                    return qs.filter(author__id=user_id)
                return qs.filter(author__id=user_id, status='PB')

            return qs.filter(
                Q(status='PB') |
                Q(status='PV', author=user)
            )

        if user_id:
            return qs.filter(author__id=user_id)
        

        return qs

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)
    

    

class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    lookup_field= 'slug'
    permission_classes = [IsPostAuthorOrStaffDeleteOrReadOnly]
    authentication_classes = [JWTCookieAuthentication]

    def get_queryset(self):
        qs = Post.objects.annotate(likes_count=Count('likes'))
        if self.request.user.is_anonymous:
            return qs.filter(status='PB')
        elif not self.request and self.request.user.is_staff:
            return qs.filter(Q(status='PB') | Q(status='PV', author=self.request.user))
        return qs
    

class ToggleLikeAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTCookieAuthentication]

    def post(self, request, *args, **kwargs):
        user = request.user
        slug = kwargs.get('slug')
        post = get_object_or_404(Post, slug=slug)

        if user == post.author:
            raise PermissionDenied("You cannot like your own post.")

        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            liked = False

        else:
            post.likes.add(user)
            liked = True

        return Response({
            'liked': liked,
            'likes_count': post.likes.count()
        })


class PostCommentListAPIView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTCookieAuthentication]
    filter_backends  = [SearchFilter, RoleFilter, OrderingFilter]
    search_fields = ['user__username']
    ordering_fields = ['created']
    ordering = ['-created']
    pagination_class = LimitOffsetPagination


    class StaffFilterSet(FilterSet):
        class Meta:
            model = Comment
            fields = ['is_active']


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
    # queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    permission_classes = [UserRolePermission]
    pagination_class = PageNumberPagination
    filter_backends = [RoleSearchFilter, RoleFilter, OrderingFilter]
    search_fields = ['username']
    ordering_fields = ['date_joined']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    
    class StaffFilterSet(FilterSet):
        class Meta:
            model = User
            fields = ['is_active', 'is_staff', 'is_superuser']

    def get_queryset(self):
        qs = User.objects.all()
        post_slug = self.request.query_params.get('slug')
        if post_slug: 
            return qs.filter(liked_posts__slug=post_slug)
        return qs