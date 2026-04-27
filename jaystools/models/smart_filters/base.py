"""Base model classes for jaystools smart filters."""

from collections import defaultdict

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from .common import _get_memberaudit_jump_clone_model


class BaseFilter(models.Model):
    """Common contract for Secure Groups smart filters."""

    name = models.CharField(
        max_length=500,
        help_text=_("The filter name that is shown to the admin."),
    )
    description = models.CharField(
        max_length=500,
        help_text=_("The filter description that is show to end users."),
    )

    class Meta:
        """Abstract base model meta for all smart filters."""

        abstract = True

    def __str__(self) -> str:
        return f"{self.name}: {self.description}"

    def process_filter(self, user: AbstractBaseUser) -> bool:
        """Evaluate this filter for a single user."""

        raise NotImplementedError(_("Please create a filter!"))

    def audit_filter(self, users: models.QuerySet) -> dict:
        """Evaluate this filter for a queryset of users with audit messages."""

        raise NotImplementedError(_("Please create an audit function !"))


class _JumpCloneBaseFilter(BaseFilter):
    """Shared ORM logic for all jump clone location filters."""

    include_alts = models.BooleanField(
        default=True,
        help_text=_(
            "When enabled, the filter checks all characters including alts. "
            "Disable to restrict to main characters only."
        ),
    )

    class Meta:
        """Abstract meta for jump clone location filters."""

        abstract = True

    def _get_configured_ids(self) -> list:
        raise NotImplementedError

    def _location_queryset_kwargs(self, ids: list) -> dict:
        raise NotImplementedError

    def process_filter(self, user: AbstractBaseUser) -> bool:
        ids = self._get_configured_ids()
        if not ids:
            return False

        character_jump_clone_model = _get_memberaudit_jump_clone_model()
        qs = character_jump_clone_model.objects.filter(
            character__eve_character__character_ownership__user=user,
            **self._location_queryset_kwargs(ids),
        )

        if not self.include_alts:
            qs = qs.filter(character__eve_character__userprofile__isnull=False)

        return qs.exists()

    def audit_filter(self, users: models.QuerySet) -> dict:
        output = {
            user_id: {"message": "", "check": False}
            for user_id in users.values_list("id", flat=True)
        }

        ids = self._get_configured_ids()
        if not ids:
            return output

        character_jump_clone_model = _get_memberaudit_jump_clone_model()
        qs = character_jump_clone_model.objects.filter(
            character__eve_character__character_ownership__user__in=list(users),
            **self._location_queryset_kwargs(ids),
        )

        if not self.include_alts:
            qs = qs.filter(character__eve_character__userprofile__isnull=False)

        matches = qs.values(
            user_id=F("character__eve_character__character_ownership__user_id"),
            character_name=F("character__eve_character__character_name"),
            location_name=F("location__name"),
        ).distinct()

        user_chars: dict = defaultdict(list)
        for row in matches:
            user_chars[row["user_id"]].append(
                f"{row['character_name']} ({row['location_name']})"
            )

        for user_id, entries in user_chars.items():
            output[user_id] = {
                "message": ", ".join(sorted(entries)),
                "check": True,
            }

        return output
