from rest_framework import serializers
from .models import Post, Comment
from .views import *



class PostSerializer(serializers.ModelSerializer):


    # def to_representation(self, instance): # status should be added in fields then pop under terms
    #     representation = super().to_representation(instance)
    #     request = self.context.get('request')
    #     representation['status'] = Post.PostStatus(instance.status).label 
    #     if not ((request and request.user.is_staff) or (request and request.user == instance.author and representation['status'] == 'Private')):
    #         representation.pop('status', None)
    #     return representation

    def to_representation(self, instance):# status shouldnt be added in fields only would be added under terms
        representation = super().to_representation(instance)
        request = self.context.get('request')

        status = Post.PostStatus(instance.status)
        status_label = status.label

        if request and (
            request.user.is_staff or
            (request.user == instance.author and status == Post.PostStatus.PRIVATE)
        ):
            representation['status'] = status_label

        return representation


    comments = serializers.HyperlinkedIdentityField(view_name='blog:comment-list', lookup_field='slug')

    class Meta:
        model = Post
        fields = ['id', 'title',  'content', 'slug', 'created', 'updated', 'author', 'image', 'comments']
        read_only_fields = ['author']


class PostCommentSerializer(serializers.ModelSerializer):

    def comment_user_info(self, obj):
        return {
            'username': obj.user.username,
            'id': obj.user.id,
        }
    
    def to_representation(self, instance):
        rp = super().to_representation(instance)
        request = self.context.get('request')
        if not (request and request.user.is_staff):
            rp.pop('is_active', None)
        return rp

    
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if not (request and request.user.is_staff):
            fields['is_active'].read_only = True
        return fields

    
    user = serializers.SerializerMethodField('comment_user_info')
    class Meta:
        model = Comment
        fields = ['id', 'user', 'body', 'created', 'is_active', 'post', 'parent']
        read_only_fields = ['user', 'parent', 'post']

    # def create(self, validated_data):# get contex passed by view then override create method or perform_create in view
    #     request= self.context.get('request')
    #     post = self.context.get('post')
    #     if request and request.user.is_authenticated:
    #         user = request.user
    #     comment = Comment.objects.create(user=user, post=post,  **validated_data)
    #     return comment

