from rest_framework import serializers
from .models import Poll, Vote, Post
from posts.serializers import PostSerializer
from django.core.exceptions import ValidationError
from textblob import TextBlob


# class RunningShoeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RunningShoe
#         fields = ['id', 'name', 'image']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['poll', 'shoe']


class PollSerializer(serializers.ModelSerializer):
    shoes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Post.objects.all()
        )
    owner = serializers.ReadOnlyField(source='owner.username')
    vote_count = serializers.ReadOnlyField()

    class Meta:
        model = Poll
        fields = [
            'id',
            'question',
            'created_at',
            'updated_at',
            'owner',
            'shoes',
            'vote_count',
            ]

    def validate_shoes(self, shoes):
        if 2 <= len(shoes) <= 4:
            return shoes
        raise serializers.ValidationError(
            "A poll must have between 2 to 4 shoe options.")

    def validate(self, data):
        question = data['question']
        shoes = data['shoes']
        if Poll.objects.filter(question=question, shoes__in=shoes).exists():
            raise serializers.ValidationError(
                "A poll with the same question and shoes already exists.")

        return data

    def validate_question(self, value):
        text_blob = TextBlob(value)
        if text_blob.correct() != text_blob:
            raise serializers.ValidationError(
                "Question contains grammatical errors. Did you mean? " + text_blob.correct())

        value = value.lower()

        return value

    def validate_repeat(self, data):
        user = self.context['request'].user
        poll = data['poll']
        if Vote.objects.filter(user=user, poll=poll).exists():
            raise serializers.ValidationError(
                "You have already voted in this poll.")
        return data

    def create(self, validated_data):
        shoe_data = validated_data.pop('shoes')
        poll = Poll.objects.create(**validated_data)
        for shoe in shoe_data:
            poll.shoes.add(shoe)

        return poll


class VoteCreateSerializer(serializers.Serializer):
    poll_id = serializers.IntegerField()
    question = serializers.CharField()
    shoes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Post.objects.all()
    )
    shoe_id = serializers.IntegerField()

    def create(self, validated_data):
        # You can implement the creation logic here if needed.
        pass