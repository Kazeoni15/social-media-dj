# I wrote this code

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse
from channels.layers import get_channel_layer
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.views import APIView
import json
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework import serializers
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .forms import SignUpForm, LoginForm
from .models import UserProfile, Post, MediaFile, Like, Comment, Friendship, ChatRoom
from .serializers import PostSerializer, FriendshipSerializer, UserSerializer, UserProfileSerializer, LikeSerializer, CommentSerializer, ChatRoomSerializer
from django.shortcuts import render, get_object_or_404



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user =user)
            login(request, user)
            return redirect('')
    else:
        form = UserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('')  # Redirect to home or any other page after login


    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('')  # Redirect to the desired page after logout


def home(request):
    followed_users = []  # Initialize an empty list for followed users

    if request.user.is_authenticated:
        user = request.user
        following = Friendship.objects.filter(follower=user).values_list('followed', flat=True)
        posts = Post.objects.filter(user__in=[user.id] + list(following)).order_by('-timestamp')

        # Fetch likes and comments for each post
        for post in posts:
            post.likes_set = Like.objects.filter(post=post)
            post.comments = Comment.objects.filter(post=post).order_by('timestamp')
            post.media = MediaFile.objects.filter(post=post)
            post.numLikes  = len(Like.objects.filter(post=post))

            # Retrieve users who liked the post
            post.liked_users = post.likes_set.values_list('user', flat=True)

        # Fetch the list of followed users
        followed_users = User.objects.filter(id__in=following)

        context = {
            'user': user,
            'posts': posts,
            'following': followed_users,
        }


    else:
        context = {
              # Send an empty list if not logged in
        }

    return render(request, 'landing/index.html', context)


class ComposePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request, *args, **kwargs):
        content = request.data.get('content')
        media_files = request.data.getlist('media')
        print("length of files" , media_files)

        # Create the post with content and associate the user
        post = Post.objects.create(user=request.user, content=content)

        # Save associated media files
        for media_file in media_files:
            # Create media files associated with the user
            if media_file != "":
                MediaFile.objects.create(post=post, file=media_file, user=request.user)
        Response({'status': 'Post created successfully'})
        return redirect('')


class FollowUser(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the friendship already exists
        if Friendship.objects.filter(follower=request.user, followed=user_to_follow).exists():
            Response({'message': 'You are already following this user.'}, status=status.HTTP_400_BAD_REQUEST)
            return redirect("")

        friendship = Friendship(follower=request.user, followed=user_to_follow)
        friendship.save()

        serializer = FriendshipSerializer(friendship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SearchUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('query', '')

        if not query:
            Response({'message': 'Query parameter "query" is required.'}, status=status.HTTP_400_BAD_REQUEST)
            return redirect('')

        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)  # Exclude the logged-in user
        serializer = UserSerializer(users, many=True)

        # Get a list of user IDs that the current user is following
        followed_users_ids = Friendship.objects.filter(follower=request.user).values_list('followed__id', flat=True)

        context = {
            'users': serializer.data,  # Pass the users data to the template
            'query': query,
            'following': followed_users_ids,  # Pass the list of followed user IDs
        }

        return render(request, 'search/results.html', context)






def user_profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        redirect("/")

    # Fetch the user's profile
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None

    # Check if the current user is viewing their own profile
    is_own_profile = request.user == user

    # Fetch all media related to the fetched user
    media_files = MediaFile.objects.filter(post__user=user)

    # Fetch posts made by the fetched user and related data
    posts = Post.objects.filter(user=user).order_by('-timestamp')
    for post in posts:
        post.likes_set = Like.objects.filter(post=post)
        post.comments = Comment.objects.filter(post=post).order_by('timestamp')
        post.media = MediaFile.objects.filter(post=post)
        post.liked_users = post.likes_set.values_list('user', flat=True)
        post.numLikes = len(Like.objects.filter(post=post))



    context = {
        'user': request.user,
        'fetchedUser': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'media_files': media_files,
        'posts': posts,
    }

    return render(request, 'personal/timeline.html', context)


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    template_name = 'personal/update.html'  # Specify the template here

    def get_object(self):
        return self.queryset.get(user=self.request.user)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return render(request, self.template_name, {'user_profile': serializer.data})

    def post(self, request, *args, **kwargs):
        # Check if a new profile picture was uploaded
        new_profile_picture = request.FILES.get('media')



        if new_profile_picture:
            # Create a new post for the profile picture
            new_post = Post.objects.create(user=request.user, content=f"{request.user.username} has updated their Profile Picture" )

            # Create a new MediaFile associated with the new post and profile picture
            new_media_file = MediaFile.objects.create(
                post=new_post,
                file=new_profile_picture,
                user=request.user
            )

            # Update the UserProfile with the new MediaFile URL
            instance = self.get_object()
            instance.profile_picture = new_media_file.file.url
            instance.save()

        # Update the UserProfile with other form data
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return redirect(f"/profile/{request.user.username}")


class LikeCreateView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = Post.objects.get(pk=post_id)

        # Check if a like by the same user on the same post already exists
        existing_like = Like.objects.filter(user=self.request.user, post=post).first()
        if existing_like:
            # You can choose to raise an exception or handle it in another way
            # For example, you can return a custom response indicating that the user already liked the post
            raise serializers.ValidationError("You already liked this post.")

        serializer.save(user=self.request.user, post=post)



class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print(self.request.user)
        post_id = self.kwargs['post_id']
        post = Post.objects.get(pk=post_id)
        serializer.save(user=self.request.user, post=post)


async def ws_connect(request, room_name):
    # Check if the user is authenticated or allowed to connect
    if request.user.is_authenticated:
        # Accept the WebSocket connection
        await request.websocket.accept()

        # Add the user to the room group (replace 'room_name' with your logic)
        room_group_name = f"chat_{room_name}"
        await request.channel_layer.group_add(
            room_group_name,
            request.channel_name
        )

        try:
            while True:
                # Wait for a message from the WebSocket
                message = await request.websocket.receive()

                # Broadcast the received message to the room group
                await request.channel_layer.group_send(
                    room_group_name,
                    {
                        'type': 'chat.message',
                        'message': message.decode('utf-8')
                    }
                )
        finally:
            # Remove the user from the room group when the WebSocket closes
            await request.channel_layer.group_discard(
                room_group_name,
                request.channel_name
            )
    else:
        # Reject the WebSocket connection if the user is not authenticated
        await request.websocket.close()

def chatPage (request):
    return render(request, 'chat/chatPage.html')


def chatRoom(request, room_id):
    # Get the ChatRoom object based on the room_id
    chat_room = ChatRoom.objects.get(pk=room_id)

    # Get the usernames of the participants in the chat room
    participants = chat_room.participants.all()

    # Separate participants into user and friend categories
    user_participant = None
    friend_participants = []

    for participant in participants:
        if participant == request.user:
            user_participant = participant
        else:
            friend_participants.append(participant)

            # print(friend_participants[0].username)
            # print(request.user.id)
    context = {

        'roomId': room_id,  # Include roomId in the context
        'chat_room': chat_room,  # Include the ChatRoom object if needed
        'user_participant': request.user,  # Include the user participant
        'friend_participant': friend_participants[0],  # Include friend participants
    }

    return render(request, 'chat/chatRoom.html', context)



class ChatRoomCreateView(generics.CreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Get the user ID from the URL parameter
        user_id = self.kwargs['user_id']
        print(request.user.id, user_id)
        # Check if a chat room already exists for these participants
        participants = [request.user.id, user_id]
        chat_room = ChatRoom.objects.filter(participants=request.user.id).filter(participants=user_id).distinct()

        if chat_room.exists():
            # A chat room already exists, return its details
            serializer = ChatRoomSerializer(chat_room.first())
            print("exists")
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create a new chat room
            chat_room = ChatRoom.objects.create()
            chat_room.participants.add(request.user, User.objects.get(pk=user_id))
            serializer = ChatRoomSerializer(chat_room)
            print("created")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Set the template_name attribute to None to indicate that no template should be used
    template_name = None

class FollowingListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]



    def get_queryset(self):
        # Get the list of users you're following
        print("called")

        following = Friendship.objects.filter(follower=self.request.user)
        following_users = following.values_list('followed', flat=True)
        return User.objects.filter(pk__in=following_users)



# end of code I wrote