from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import SignUpForm
from .models import Friendship, Post, Like, Comment, UserProfile, MediaFile, ChatRoom
from django.contrib.auth import authenticate, login, logout
from django.test.client import Client
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework.test import APITestCase, APIRequestFactory
from .serializers import UserSerializer


class SignupViewTests(TestCase):
    def test_signup_view_with_valid_data(self):
        # Test the signup view with valid form data
        data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('signup'), data)


        # Check if a new user is created in the database
        user_exists = User.objects.filter(username='testuser').exists()


    def test_signup_view_with_invalid_data(self):
        # Test the signup view with invalid form data
        data = {
            'username': '',  # Invalid: Username is required
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)  # Stay on the signup page

        # Check if no new user is created in the database
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertFalse(user_exists)

        # Check if the user is not logged in
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_signup_view_with_existing_username(self):
        # Test the signup view with an existing username
        # Create a user with the same username
        User.objects.create_user(username='testuser', password='testpassword')
        data = {
            'username': 'testuser',  # Existing username
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('signup'), data)
        self.assertEqual(response.status_code, 200)  # Stay on the signup page

        # Check if no new user is created in the database
        user_count = User.objects.filter(username='testuser').count()
        self.assertEqual(user_count, 1)  # Should still have only one user

        # Check if the user is not logged in
        self.assertFalse('_auth_user_id' in self.client.session)


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_user_login_valid_credentials(self):

        # Test user login with valid credentials.

        # Create a client and log in the user
        client = Client()
        response = client.post(reverse('login'), {'username': self.username, 'password': self.password})

        # Check if the user is logged in and redirected to the home page
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(response.url, reverse(''))  # Check the redirection URL

        # Check if the user is logged in
        user = authenticate(username=self.username, password=self.password)
        self.assertTrue(user.is_authenticated)

    def test_user_login_invalid_credentials(self):

        # Test user login with invalid credentials.

        # Create a client and attempt to log in with invalid credentials
        client = Client()
        response = client.post(reverse('login'), {'username': self.username, 'password': 'wrongpassword'})

        # Check if the login failed and the user is not redirected
        self.assertEqual(response.status_code, 200)  # Login page should be reloaded


    def test_user_logout(self):

        # Test user logout.

        # Create a client and log in the user
        client = Client()
        client.login(username=self.username, password=self.password)

        # Check if the user is initially logged in
        user = authenticate(username=self.username, password=self.password)
        self.assertTrue(user.is_authenticated)

        # Perform user logout
        response = client.get(reverse('logout'))

        # Check if the user is logged out and redirected to the home page
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(response.url, reverse(''))  # Check the redirection URL



class HomeViewTestCase(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_home_view_authenticated_user(self):

        # Test the home view for an authenticated user.

        # Create some test data - friends, posts, likes, and comments
        friend1 = User.objects.create_user(username="friend1", password="testpassword")
        friend2 = User.objects.create_user(username="friend2", password="testpassword")
        Friendship.objects.create(follower=self.user, followed=friend1)
        Friendship.objects.create(follower=self.user, followed=friend2)

        post1 = Post.objects.create(user=friend1, content="Post by friend1")
        post2 = Post.objects.create(user=friend2, content="Post by friend2")
        post3 = Post.objects.create(user=self.user, content="Post by authenticated user")





        response = self.client.get(reverse(''))

        # Check if the response contains the posts, likes, comments, and followed users
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Post by friend1")
        self.assertContains(response, "Post by friend2")
        self.assertContains(response, "Post by authenticated user")



    def test_home_view_unauthenticated_user(self):

        # Test the home view for an unauthenticated user.

        # Log out the user
        self.client.logout()

        response = self.client.get(reverse(''))


class FollowUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_to_follow = User.objects.create_user(username='user_to_follow', password='password')
        self.client.login(username='testuser', password='testpassword')

    def test_follow_user(self):
        url = reverse('follow_user', args=[self.user_to_follow.id])  # Replace with the actual URL name
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the friendship was created in the database
        self.assertTrue(Friendship.objects.filter(follower=self.user, followed=self.user_to_follow).exists())



    def test_follow_user_user_not_found(self):
        non_existent_user_id = 999  # An ID that does not exist in the User model
        url = reverse('follow_user', args=[non_existent_user_id])  # Replace with the actual URL name
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('User not found.', response.data['message'])


class SearchUserTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.user_to_find = User.objects.create_user(username='user_to_find', password='password')
        self.user_not_to_find = User.objects.create_user(username='not_to_find', password='password')
        Friendship.objects.create(follower=self.user, followed=self.user_to_find)

    def test_search_user(self):
        # test search
        url = reverse('search-user')
        query = 'user_to_find'
        response = self.client.get(f"{url}?query={query}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)



class UserProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.fetched_user = User.objects.create_user(username='fetcheduser', password='testpassword')
        self.profile = UserProfile.objects.create(user=self.fetched_user, bio='Test Bio')
        self.post = Post.objects.create(user=self.fetched_user, content='Test Content')
        self.media_file = MediaFile.objects.create(post=self.post, file='test.jpg', user=self.fetched_user)
        self.like = Like.objects.create(user=self.user, post=self.post)
        self.comment = Comment.objects.create(user=self.user, post=self.post, content='Test Comment')

    def test_user_profile_view(self):
        url = reverse('user_profile', args=[self.fetched_user.username])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.fetched_user.username)
        self.assertContains(response, 'Test Bio')
        self.assertContains(response, 'Test Content')
        self.assertContains(response, 'Test Comment')

    def test_user_profile_view_own_profile(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('user_profile', args=[self.user.username])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)






class UserProfileUpdateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user, bio='Test Bio')


    def test_user_profile_update_view(self):
        url = reverse('update_profile', args=[self.user.username])
        data = {
            'bio': 'Updated Bio',

        }

        response = self.client.post(url, data, format='multipart')

        self.assertEqual(response.status_code, 302)  # Redirect status code
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, 'Updated Bio')


class FollowingListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.user3 = User.objects.create_user(username='user3', password='password3')

        # Create friendships between user1 and user2, and user1 and user3
        Friendship.objects.create(follower=self.user1, followed=self.user2)
        Friendship.objects.create(follower=self.user1, followed=self.user3)

    def test_following_list_view(self):
        self.client.login(username='user1', password='password1')
        url = reverse('following-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
