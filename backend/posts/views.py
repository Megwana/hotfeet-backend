from django.db.models import Count
from rest_framework import generics, permissions, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from backend.permissions import IsOwnerOrReadOnly
from .models import Post
from .serializers import PostSerializer
from rest_framework.response import Response
from spellchecker import SpellChecker


class PostList(generics.ListCreateAPIView):
    """
    List posts or create a post if logged in
    The perform_create method associates the post with the logged in user.
    """
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Post.objects.annotate(
        comments_count=Count('owner__comment', distinct=True),
        likes_count=Count('owner__like', distinct=True)
    ).order_by('-created_at')
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        'owner__followed__owner__profile',
        'likes__owner__profile',
        'owner__profile',
    ]
    search_fields = [
        'owner__username',
        'title',
    ]
    ordering_fields = [
        'likes_count',
        'comments_count',
        'likes__created_at',
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

def is_gibberish(text):
    # Count consecutive consonants, consecutive vowels, and the ratio of vowels to consonants
    consecutive_consonants = 0
    consecutive_vowels = 0
    total_consonants = 0
    total_vowels = 0

    for char in text:
        if char.isalpha():
            if char.lower() not in 'aeiou':
                consecutive_consonants += 1
                consecutive_vowels = 0
                total_consonants += 1
            else:
                consecutive_vowels += 1
                consecutive_consonants = 0
                total_vowels += 1

            if consecutive_consonants >= 5 or consecutive_vowels >= 5:
                return True

    gibberish_threshold = 0.5

    if total_consonants == 0:
        return False

    vowel_consonant_ratio = total_vowels / total_consonants
    return vowel_consonant_ratio > gibberish_threshold


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve a post and edit or delete it if you own it.
    """
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Post.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            title = request.data.get('title')
            content = request.data.get('content')

            if is_gibberish(title) or is_gibberish(content):
                return Response(
                    {"detail": "Post cannot be changed to gibberish, please review"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)