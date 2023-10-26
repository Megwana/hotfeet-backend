from rest_framework import generics, permissions
from backend.permissions import IsOwnerOrReadOnly
from .models import Poll, Vote
from .serializers import PollSerializer, VoteSerializer


class PollList(generics.ListCreateAPIView):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Poll.objects.all()

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


class VoteCreate(generics.CreateAPIView):
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
