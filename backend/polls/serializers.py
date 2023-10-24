from rest_framework import serializers
from .models import Poll, Vote, RunningShoe


class RunningShoeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RunningShoe
        fields = ['id', 'name', 'image']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['user', 'poll', 'shoe']


class PollSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)
    shoes = RunningShoeSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = [
            'id',
            'question',
            'created_at',
            'updated_at',
            'owner',
            'votes',
            'shoes'
            ]
