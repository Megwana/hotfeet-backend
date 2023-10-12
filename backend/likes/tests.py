from django.contrib.auth.models import User
from likes.models import Like
from posts.models import Post
from rest_framework import status
from rest_framework.test import APITestCase


class LikeListViewTests(APITestCase):
    def setUp(self):
        self.adam = User.objects.create_user(username='adam', password='pass')
        self.brian = User.objects.create_user(username='brian', password='pass')
        self.test_post = Post.objects.create(owner=self.adam, title="Test Post")
        Like.objects.create(owner=self.adam, post=self.test_post)
        Like.objects.create(owner=self.brian, post=self.test_post)

    def test_can_list_likes(self):
        new_post = Post.objects.create(owner=self.adam, title="Test Post 1")
        Like.objects.create(owner=self.adam, post=new_post)
        response = self.client.get('/likes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_logged_in_user_can_create_like(self):
        new_post = Post.objects.create(owner=self.brian, title="New Test Post")

        self.client.login(username='adam', password='pass')
        response = self.client.post('/likes/', {"post": new_post.id})

        count = Like.objects.count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_not_logged_in_cant_create_like(self):
        response = self.client.post('/likes/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LikeDetailViewTests(APITestCase):
    def setUp(self):
        self.adam = User.objects.create_user(username='adam', password='pass')
        self.brian = User.objects.create_user(username='brian', password='pass')
        self.test_post = Post.objects.create(owner=self.adam, title="Test Post")
        Like.objects.create(owner=self.adam, post=self.test_post)
        Like.objects.create(owner=self.brian, post=self.test_post)

    def test_can_retrieve_like_using_valid_id(self):
        response = self.client.get('/likes/1/')
        self.assertEqual(response.data['owner'], 'adam')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_retrieve_like_using_invalid_id(self):
        response = self.client.get('/likes/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_delete_own_like(self):
        self.client.login(username='adam', password='pass')
        response = self.client.delete('/likes/1/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Like.objects.filter(pk=1).exists())

    def test_user_cant_delete_another_users_like(self):
        self.client.login(username='adam', password='pass')
        response = self.client.delete('/likes/2/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
