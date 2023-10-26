from rest_framework import serializers
from .models import Poll, Vote, RunningShoe, Post
from posts.serializers import PostSerializer


class RunningShoeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunningShoe
        fields = ['id', 'name', 'image']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['user', 'poll', 'shoe']


class PollSerializer(serializers.ModelSerializer):
    shoes = serializers.PrimaryKeyRelatedField(many=True, queryset=Post.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Poll
        fields = [
            'id',
            'question',
            'created_at',
            'updated_at',
            'owner',
            'shoes'
            ]

    def validate_shoes(self, shoes):
        if 2 <= len(shoes) <= 4:
            return shoes
        raise serializers.ValidationError(
            "A poll must have between 2 to 4 shoe options.")

    def create(self, validated_data):
        shoe_data = validated_data.pop('shoes')
        poll = Poll.objects.create(**validated_data)

        for shoe in shoe_data:
            RunningShoe.objects.create(poll=poll, **shoe)

        return poll
