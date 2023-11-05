from django.contrib import admin
from .models import Poll, Vote

class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'owner', 'created_at', 'updated_at', 'vote_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('question', 'owner__username')

class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'shoe')
    list_filter = ('poll',)
    search_fields = ('user__username', 'poll__question', 'shoe__name')

admin.site.register(Poll, PollAdmin)
admin.site.register(Vote, VoteAdmin)
