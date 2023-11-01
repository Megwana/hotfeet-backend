from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.permissions import IsOwnerOrReadOnly
from .models import Poll, Vote, RunningShoe
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .serializers import PollSerializer, VoteSerializer
from django.db.models import Count, F


class PollList(generics.ListCreateAPIView):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Poll.objects.all()
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_fields = [
        'vote_count',
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PollDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Poll.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user:
            return Response({
                "error": "You don't have permission to change this poll."
                }, status=HTTP_403_FORBIDDEN)

        return super(PollDetail, self).update(request, *args, **kwargs)


class PollVoteList(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]


class VoteCreate(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        poll_id = self.request.data.get('poll')
        try:
            poll = Poll.objects.get(pk=poll_id)
            context['poll'] = poll
            context['available_shoes'] = poll.shoes.all()
        except Poll.DoesNotExist:
            context['poll'] = None
            context['available_shoes'] = []
        return context

    def create(self, request, *args, **kwargs):
        user = request.user
        poll = self.get_serializer_context()['poll']
        shoe = self.get_serializer_context()['available_shoes'].filter(
            pk=request.data['shoe']).first()

        if not poll or not shoe:
            return Response(
                {"error": "Invalid poll or shoe selection."},
                status=status.HTTP_400_BAD_REQUEST
                )

        # Check if the user has already voted in this poll
        has_voted = Vote.objects.filter(user=user, poll=poll).exists()

        if has_voted:
            existing_vote = Vote.objects.get(user=user, poll=poll)
            if existing_vote.shoe == shoe:
                # User is trying to vote for the same shoe again, reject vote
                return Response(
                    {"error": "You have already voted for this running shoe."},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # User has voted before, update their vote to a different shoe
                serializer = self.get_serializer(
                    existing_vote, data=request.data,
                    partial=True
                    )
                serializer.is_valid(raise_exception=True)
                serializer.save()
        else:
            # User is voting for the first time in this poll
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)

            # Increment vote count in the poll using F expression
            Poll.objects.filter(pk=poll.pk).update(
                vote_count=F('vote_count') + 1)

        return Response(
            {"message": "Your vote has been recorded."},
            status=status.HTTP_201_CREATED
            )
