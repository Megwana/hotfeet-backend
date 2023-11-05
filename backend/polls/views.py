from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.permissions import IsOwnerOrReadOnly
from .models import Poll, Vote
from .serializers import VoteSerializer, PollSerializer, ShoeSerializer
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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        serialized_data = serializer.data
        serialized_data['question'] = instance.question

        return Response(serialized_data)


class PollVoteList(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated]


class VoteCreate(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        poll_id = self.kwargs['poll_id']
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise ValidationError(
                {"detail": "Selected poll does not exist."},
                code="not_found"
            )

        available_shoes = poll.shoes.all()
        if available_shoes.exists():
            available_shoes_data = ShoeSerializer(available_shoes, many=True).data
            shoe_id = request.data.get('shoe')
            shoe = available_shoes.filter(pk=shoe_id).first()

            if not shoe:
                return Response(
                    {"Error": "Invalid shoe selection for this poll."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            has_voted = Vote.objects.filter(user=user, poll=poll).exists()

            if has_voted:
                existing_vote = Vote.objects.get(user=user, poll=poll)
                if existing_vote.shoe == shoe:
                    return Response(
                        {"Error": "You have already voted for this running shoe."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    serializer = self.get_serializer(
                        existing_vote, data=request.data,
                        partial=True
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
            else:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=user, poll=poll)

                # Increment vote count in the poll
                poll.update_vote_count(increment=1)

                return Response(
                    {"Message": "Your vote has been recorded. Poll vote count: {}".format(poll.vote_count)},
                    status=status.HTTP_201_CREATED
                )
        else:
            return Response(
                {"Error": "No options (shoes) available for this poll."},
                status=status.HTTP_400_BAD_REQUEST
            )

class VoteDelete(generics.DestroyAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        poll_id = self.kwargs['poll_id']
        try:
            return get_object_or_404(Vote, user=user, poll_id=poll_id)
        except Poll.DoesNotExist:
            raise ValidationError(
                {"detail": "Selected poll does not exist."},
                code="not_found"
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        poll = instance.poll
        current_vote_count = poll.vote_count
        # Decrement the poll's vote_count
        poll.update_vote_count(increment=-1)
        # Delete the vote
        self.perform_destroy(instance)
        # Return the updated vote count in the response
        return Response({
            "Message": "Your vote has been removed.",
            "Updated vote count for the poll": current_vote_count - 1
        }, status=status.HTTP_204_NO_CONTENT)