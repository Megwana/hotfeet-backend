def vote_in_poll(user, poll, shoe):
    try:
        # check if user has already voted in this poll
        existing_vote = Vote.objects.get(user=user, poll=poll)
        return None
    except Vote.DoesNotExist:
        # The user has not voted in this poll, continue to vote
        vote = Vote.objects.create(user=user, poll=poll, shoe=shoe)
        # Increment the vote count in the poll for selected shoe
        poll.vote_count += 1
        poll.save()
        return vote