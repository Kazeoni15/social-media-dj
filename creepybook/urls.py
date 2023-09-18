from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('signup/', signup, name='signup'),
    path('', home, name=''),
    path('chats/', chatPage, name='chatPage'),
    path('api/post/', ComposePostView.as_view(), name='compose_post' ),
    path('searchUser/', SearchUser.as_view(), name='search-user'),
    path('follow_user/<int:user_id>/', FollowUser.as_view(), name='follow_user'),
    path('profile/<str:username>/', user_profile, name='user_profile'),
    path('profile/update/<str:username>/', UserProfileUpdateView.as_view(), name='update_profile'),
    path('like/<int:post_id>/', LikeCreateView.as_view(), name='like-create'),
    path('comment/<int:post_id>/', CommentCreateView.as_view(), name='comment-create'),
    path('api/following/', FollowingListView.as_view(), name='following-list'),
    path('chat-room/<int:room_id>/', chatRoom , name='chat-room-create'),
    path('api/check-create-chat-room/<int:user_id>/', ChatRoomCreateView.as_view(), name='chat-room-create'),




    # ...
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
