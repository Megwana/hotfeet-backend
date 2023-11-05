from django.db import models
from django.contrib.auth.models import User
from posts.models import Post


class Poll(models.Model):
    question = models.CharField(max_length=250)
    shoes = models.ManyToManyField(Post, related_name='polls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.question
    
    def update_vote_count(self, increment=1):
        # Update the vote count, ensuring it never goes below 0
        self.vote_count = max(self.vote_count + increment, 0)
        self.save()


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(
        Poll,
        related_name='votes',
        on_delete=models.CASCADE)
    shoe = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'poll', 'shoe')
