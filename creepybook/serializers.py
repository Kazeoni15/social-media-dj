from rest_framework import serializers
from .models import MediaFile, Post, Friendship, UserProfile, Like, Comment, ChatRoom
from django.contrib.auth.models import User



class PostSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    media = serializers.ListField(child=serializers.ImageField(), required=False)


class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(max_length=None, use_url=True)
    class Meta:
        model = UserProfile
        fields = ['bio', 'birthdate', 'website', 'profile_picture']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'