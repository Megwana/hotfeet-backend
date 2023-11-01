from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from backend.permissions import IsOwnerOrReadOnly
from .models import Poll, Vote, RunningShoe
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from .serializers import PollSerializer, VoteSerializer


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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def vote(request, poll_id):
        poll = get_object_or_404(Poll, pk=poll_id)

        if request.method == 'POST':
            shoe_id = request.POST['shoe']
            shoe = get_object_or_404(RunningShoe, pk=shoe_id)

            # Check if the user has already voted in this poll
            if Vote.objects.filter(user=request.user, poll=poll).exists():
                return HttpResponse("You have already voted in this poll.")
            else:
                # Create a new vote
                Vote.objects.create(user=request.user, poll=poll, shoe=shoe)
                # Update the poll's vote count
                poll.vote_count += 1
                poll.save()
                return redirect('poll_detail', poll_id=poll.id)

        return render(request, 'polls/vote.html', {'poll': poll})