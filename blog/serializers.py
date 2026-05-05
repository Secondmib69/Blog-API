from rest_framework import serializers
from .models import Post, Comment
from .views import *
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()
class PostSerializer(serializers.ModelSerializer):


    def to_representation(self, instance): # status should be added in fields then pop under terms
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation['status'] = Post.PostStatus(instance.status).label 
        if not ((request and request.user.is_staff) or (request and request.user == instance.author)):
            representation.pop('status', None)
        return representation


    comments = serializers.HyperlinkedIdentityField(view_name='blog:comment-list', lookup_field='slug')

    class Meta:
        model = Post
        fields = ['id', 'title',  'content', 'slug', 'created', 'updated', 'author', 'image', 'comments', 'status']
        read_only_fields = ['author']


class PostCommentSerializer(serializers.ModelSerializer):
    
    user = serializers.SerializerMethodField('comment_user_info')
    class Meta:
        model = Comment
        fields = ['id', 'user', 'body', 'created', 'post', 'parent', 'is_active']
        read_only_fields = ['user', 'parent', 'post']

    def comment_user_info(self, obj):
        return {
            'username': obj.user.username,
            'id': obj.user.id,
        }
    
    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if not (request and request.user.is_staff):
            fields.pop('is_active') # representation manages output but get_fields manages fields
        return fields
    
    # def create(self, validated_data):# get contex passed by view then override create method or perform_create in view
    #     request= self.context.get('request')
    #     post = self.context.get('post')
    #     if request and request.user.is_authenticated:
    #         user = request.user
    #     comment = Comment.objects.create(user=user, post=post,  **validated_data)
    #     return comment


class CommentApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ['id', 'user', 'body', 'created', 'post', 'parent', 'is_active']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context["request"]

        if request.user.is_staff:
            for name, field in fields.items():
                if name != "is_active":
                    field.read_only = True
        return fields


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'job_title', 'bio', 'phone', 'is_active', 'is_staff', 'is_superuser']


    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        if request and not request.user.is_staff:
            allowed_fields = ['username', 'first_name', 'last_name', 'job_title', 'bio']
            fields =  {k: v for k, v in fields.items() if k in allowed_fields}
        
        for name, field in fields.items():
            if name not in ('is_active', 'is_staff'):
                field.read_only = True

        return fields