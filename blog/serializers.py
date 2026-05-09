from rest_framework.reverse import reverse
from rest_framework import serializers
from .models import Post, Comment
from .views import *
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()
class PostSerializer(serializers.ModelSerializer):


    def get_likes(self, obj):
        request = self.context.get('request')
        url = reverse('blog:user-list', request=request)

        return f'{url}?slug={obj.slug}'
    
    def get_author(self, obj):
        request = self.context.get('request')
        url = reverse('blog:user-detail', request=request, kwargs={'pk': obj.author.id})
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'profile': url
        }
    author = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    comments = serializers.HyperlinkedIdentityField(view_name='blog:comment-list', lookup_field='slug')

    class Meta:
        model = Post
        fields = ['id', 'title',  'content', 'slug', 'created', 'updated', 'author', 'image', 'comments', 'likes_count', 'likes', 'status']
        read_only_fields = ['author']

    def to_representation(self, instance): # status should be added in fields then pop under terms
        representation = super().to_representation(instance)
        request = self.context.get('request')
        representation['status'] = Post.PostStatus(instance.status).label 
        if not ((request and request.user.is_staff) or (request and request.user == instance.author)):
            representation.pop('status', None)
            representation.pop('likes', None)
        return representation

class PostCommentSerializer(serializers.ModelSerializer):
    
    user = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id', 'user', 'body', 'created', 'post', 'is_active']
        read_only_fields = ['user', 'post']

    def get_user(self, obj):
        request = self.context.get('request')
        url = reverse('blog:user-detail', request=request, kwargs={'pk': obj.user.id})
        return {
            'username': obj.user.username,
            'profile': url
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
        fields = ['id', 'user', 'body', 'created', 'post', 'is_active']

    def get_fields(self):
        fields = super().get_fields()
        request = self.context["request"]

        if request.user.is_staff:
            for name, field in fields.items():
                if name != "is_active":
                    field.read_only = True
        return fields


class UserSerializer(serializers.ModelSerializer):

    posts = serializers.SerializerMethodField()

    def get_posts(self, obj):
        request = self.context.get('request')
        user_id = obj.id
        link = reverse('blog:post-list', request=request) # only rest_framewok.reverse pass the request not django.urls.reverse
        return f'{link}?user_id={user_id}' # if use django reverse should use request.build_absolute_uri method 

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'job_title', 'bio', 'phone', 'posts', 'is_active', 'is_staff', 'is_superuser']


    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        view = self.context.get('view')
        user = request.user
        read_only = []

        if request and user == self.instance:
            if user.is_superuser:
                pass
            else:
                read_only += ['is_active', 'is_staff', 'is_superuser']
        elif request and user.is_superuser:
            read_only += ['id', 'username', 'first_name', 'last_name', 'email', 'job_title', 'bio', 'phone']
        elif request and user.is_staff:
            read_only += ['id', 'username', 'first_name', 'last_name', 'email', 'job_title', 'bio', 'phone', 'is_staff', 'is_superuser']


        for n, f in fields.items():
            if n in read_only:
                f.read_only = True
   
        return fields
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        if request and not request.user.is_staff:
            allowed_fields = ['username', 'first_name', 'last_name', 'job_title', 'bio', 'posts']
            if request.user == instance:
                allowed_fields += ['id', 'email', 'phone']
            rep =  {k: v for k, v in rep.items() if k in allowed_fields}

        return rep
    

class UserCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(validators=[validate_password], write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2', 'phone', 'is_active', 'is_staff', 'is_superuser']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('passwords dont match')
        return attrs


    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user