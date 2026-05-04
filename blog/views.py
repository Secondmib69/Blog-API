from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from rest_framework import generics
from .serializers import PostSerializer, PostCommentSerializer
from django.db.models import Q
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import IsAuthenticated
# Create your views here.



class PostListAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Post.objects.all()
        if not self.request.user.is_staff:
            return qs.filter(Q(status='PB') | Q(status='PV', author=self.request.user))
        return qs

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field= 'slug'


class PostCommentListAPIView(generics.ListCreateAPIView):
    serializer_class = PostCommentSerializer

    def get_queryset(self):
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
        qs = Comment.objects.filter(post=post)
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