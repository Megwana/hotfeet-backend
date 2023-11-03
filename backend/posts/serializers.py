from rest_framework import serializers
from posts.models import Post
from likes.models import Like
from textblob import TextBlob

def is_gibberish(text):

    consecutive_consonants = 0
    max_consecutive_consonants = 5

    for char in text:
        if char.isalpha():
            if char.lower() not in 'aeiou':
                consecutive_consonants += 1
            else:
                consecutive_consonants = 0
            if consecutive_consonants >= max_consecutive_consonants:
                return True

    return False

class PostSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    like_id = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField()
    comments_count = serializers.ReadOnlyField()

    def validate(self, data):
        title_blob = TextBlob(data['title'])
        content_blob = TextBlob(data['content'])

        if is_gibberish(data['title']):
            raise serializers.ValidationError("Title contains gibberish, please review.")

        if is_gibberish(data['content']):
            raise serializers.ValidationError("Content contains gibberish, please review.")

        return data
    
    def find_typos(text):
        spell = SpellChecker()
        words = text.split()
        typos = set()

        for word in words:
            if not spell.correction(word) == word:
                typos.add(word)

        return typos

    def validate_image(self, value):
        if value.size > 1024 * 1024 * 2:
            raise serializers.ValidationError(
                'Image size larger than 2MB!'
            )
        if value.image.width > 4096:
            raise serializers.ValidationError(
                'Image width larger than 4096px'
            )
        if value.image.height > 4096:
            raise serializers.ValidationError(
                'Image height larger than 4096px'
            )
        return value

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def get_like_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            like = Like.objects.filter(
                owner=user, post=obj
            ).first()
            return like.id if like else None
        return None

    class Meta:
        model = Post
        fields = [
            'id', 'owner', 'is_owner', 'profile_id',
            'profile_image', 'created_at', 'updated_at',
            'title', 'content', 'image', 'like_id',
            'likes_count', 'comments_count',
        ]
