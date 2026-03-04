from django.contrib import admin
from .models import (
    Tournament, TournamentMembership, TournamentInvite, Nomination,
    Entrant, Stage, Group, GroupEntrant, Match, Vote, GroupStanding
)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "visibility", "public_slug", "created_at")
    list_filter = ("status", "visibility")
    search_fields = ("name", "public_slug")

@admin.register(TournamentMembership)
class TournamentMembershipAdmin(admin.ModelAdmin):
    list_display = ("tournament", "user", "role", "created_at")
    list_filter = ("role", "tournament")

@admin.register(TournamentInvite)
class TournamentInviteAdmin(admin.ModelAdmin):
    list_display = ("email", "tournament", "status", "expires_at")
    list_filter = ("status", "tournament")

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ("name", "tournament", "submitted_by", "status", "created_at")
    list_filter = ("status", "tournament")

@admin.register(Entrant)
class EntrantAdmin(admin.ModelAdmin):
    list_display = ("name", "tournament")
    list_filter = ("tournament",)

@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("name", "tournament", "index")
    list_filter = ("tournament",)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "stage")
    list_filter = ("stage__tournament", "stage")

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("home_entrant", "away_entrant", "state", "stage", "group", "closes_at")
    list_filter = ("state", "stage__tournament", "stage", "group")

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("user", "match", "chosen_entrant", "created_at")
    list_filter = ("match__stage__tournament", "match")

@admin.register(GroupStanding)
class GroupStandingAdmin(admin.ModelAdmin):
    list_display = ("entrant", "group", "points")
    list_filter = ("group__stage__tournament", "group")

admin.site.register(GroupEntrant)
