from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


# ---------- Choices ----------

class TournamentStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    NOMINATION = "nomination", "Nomination"
    GROUP = "group", "Group stage"
    KNOCKOUT = "knockout", "Knockout"
    COMPLETE = "complete", "Complete"


class TournamentVisibility(models.TextChoices):
    PRIVATE = "private", "Private"
    PUBLIC_RESULTS = "public_results", "Public results"


class MembershipRole(models.TextChoices):
    HOST = "host", "Host"
    PARTICIPANT = "participant", "Participant"


class MembershipStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    REMOVED = "removed", "Removed"
    BANNED = "banned", "Banned"


class InviteStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"


class NominationStatus(models.TextChoices):
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class StageType(models.TextChoices):
    GROUP = "group", "Group"
    KNOCKOUT = "knockout", "Knockout"


class StageStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACTIVE = "active", "Active"
    COMPLETE = "complete", "Complete"


class MatchState(models.TextChoices):
    SCHEDULED = "scheduled", "Scheduled"
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    FINALIZED = "finalized", "Finalized"
    PUBLISHED = "published", "Published"


# ---------- Core Models ----------

class Tournament(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tournaments_created",
    )

    status = models.CharField(
        max_length=20,
        choices=TournamentStatus.choices,
        default=TournamentStatus.DRAFT,
        db_index=True,
    )

    visibility = models.CharField(
        max_length=20,
        choices=TournamentVisibility.choices,
        default=TournamentVisibility.PRIVATE,
        db_index=True,
    )

    public_slug = models.SlugField(max_length=64, unique=True, blank=True)
    public_enabled_at = models.DateTimeField(null=True, blank=True)

    time_zone = models.CharField(max_length=64, default="Europe/London")
    nomination_limit_per_participant = models.PositiveIntegerField(default=5)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["visibility", "public_slug"]),
        ]

    def __str__(self) -> str:
        return self.name


class TournamentMembership(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tournament_memberships"
    )

    role = models.CharField(
        max_length=20, choices=MembershipRole.choices, default=MembershipRole.PARTICIPANT, db_index=True
    )
    status = models.CharField(
        max_length=20, choices=MembershipStatus.choices, default=MembershipStatus.ACTIVE, db_index=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tournament", "user"],
                name="uq_membership_tournament_user",
            )
        ]
        indexes = [
            models.Index(fields=["tournament", "status", "role"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} in {self.tournament} ({self.role}/{self.status})"


class TournamentInvite(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="invites"
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tournament_invites_sent",
    )

    email = models.EmailField(db_index=True)
    role = models.CharField(
        max_length=20, choices=MembershipRole.choices, default=MembershipRole.PARTICIPANT
    )

    token_hash = models.CharField(max_length=128, unique=True)

    status = models.CharField(
        max_length=20, choices=InviteStatus.choices, default=InviteStatus.PENDING, db_index=True
    )
    expires_at = models.DateTimeField(db_index=True)

    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tournament_invites_accepted",
        null=True,
        blank=True,
    )
    accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["tournament", "status"]),
            models.Index(fields=["email", "status"]),
        ]

    def __str__(self) -> str:
        return f"Invite to {self.email} for {self.tournament} ({self.status})"


class Nomination(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="nominations"
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="nominations_submitted"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=20, choices=NominationStatus.choices, default=NominationStatus.SUBMITTED, db_index=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="nominations_reviewed",
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["tournament", "status"]),
            models.Index(fields=["tournament", "submitted_by"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"


class Entrant(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="entrants"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    approved_from_nomination = models.OneToOneField(
        Nomination,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entrant",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["tournament", "is_active"]),
        ]

    def __str__(self) -> str:
        return self.name


class Stage(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="stages"
    )

    type = models.CharField(max_length=20, choices=StageType.choices, db_index=True)
    index = models.PositiveIntegerField(db_index=True)  # 1=group, 2=knockout
    name = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20, choices=StageStatus.choices, default=StageStatus.PENDING, db_index=True
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["index"]
        constraints = [
            models.UniqueConstraint(fields=["tournament", "index"], name="uq_stage_tournament_index")
        ]
        indexes = [
            models.Index(fields=["tournament", "type", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.tournament.name} - {self.name}"


class Group(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=50)  # e.g. A, B, C

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["stage", "name"], name="uq_group_stage_name")
        ]

    def __str__(self) -> str:
        return f"{self.stage.name} - {self.name}"


class GroupEntrant(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_entrants")
    entrant = models.ForeignKey(Entrant, on_delete=models.CASCADE, related_name="group_participations")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["group", "entrant"], name="uq_groupentrant_group_entrant")
        ]
        indexes = [
            models.Index(fields=["group"]),
            models.Index(fields=["entrant"]),
        ]

    def __str__(self) -> str:
        return f"{self.entrant.name} in {self.group.name}"


class Match(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="matches")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name="matches", null=True, blank=True)

    home_entrant = models.ForeignKey(Entrant, on_delete=models.PROTECT, related_name="home_matches")
    away_entrant = models.ForeignKey(Entrant, on_delete=models.PROTECT, related_name="away_matches")

    opens_at = models.DateTimeField(db_index=True)
    closes_at = models.DateTimeField(db_index=True)

    state = models.CharField(
        max_length=20, choices=MatchState.choices, default=MatchState.SCHEDULED, db_index=True
    )

    # Computed results (set on finalize)
    result_home_votes = models.PositiveIntegerField(default=0)
    result_away_votes = models.PositiveIntegerField(default=0)
    winner_entrant = models.ForeignKey(
        Entrant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="won_matches",
    )

    tie_extension_used = models.BooleanField(default=False)
    decided_by_host = models.BooleanField(default=False)

    finalized_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # host reveal ordering
    sequence = models.PositiveIntegerField(default=0, db_index=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["state", "closes_at"]),
            models.Index(fields=["stage", "state"]),
            models.Index(fields=["group", "state"]),
        ]

    def __str__(self) -> str:
        return f"{self.home_entrant} vs {self.away_entrant} ({self.state})"


class Vote(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="votes")
    chosen_entrant = models.ForeignKey(Entrant, on_delete=models.PROTECT, related_name="votes_received")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["match", "user"], name="uq_vote_match_user")
        ]
        indexes = [
            models.Index(fields=["match"]),
            models.Index(fields=["user"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} voted in {self.match_id}"


class GroupStanding(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="standings")
    entrant = models.ForeignKey(Entrant, on_delete=models.CASCADE, related_name="group_standings")

    played = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

    votes_for = models.PositiveIntegerField(default=0)
    votes_against = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["group", "entrant"], name="uq_groupstanding_group_entrant")
        ]
        indexes = [
            models.Index(fields=["group"]),
            models.Index(fields=["entrant"]),
        ]

    def __str__(self) -> str:
        return f"{self.entrant.name} in {self.group.name}: {self.points}pts"