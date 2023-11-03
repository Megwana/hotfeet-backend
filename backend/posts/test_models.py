from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post
from django.core.exceptions import ValidationError

class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Bob', password='pass')

    def test_create_post(self):
        post = Post(
            owner=self.user,
            title='Test Title',
            content='Test Content',
        )
        post.save()

        # Retrieve the saved post
        retrieved_post = Post.objects.get(id=post.id)

        self.assertEqual(retrieved_post.title, 'Test Title')
        self.assertEqual(retrieved_post.content, 'Test Content')
        self.assertEqual(retrieved_post.owner, self.user)

    def test_custom_str_method(self):
        post = Post(
            owner=self.user,
            title='Custom String Method Test',
            content='Test Content',
        )
        post.save()

        self.assertEqual(str(post), f'{post.id} Custom String Method Test')