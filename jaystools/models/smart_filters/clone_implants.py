"""MemberAudit jump-clone implant smart filter for jaystools."""

from collections import defaultdict

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _

from .base import BaseFilter
from .common import _get_memberaudit_jump_clone_implant_model
from .common import _parse_ids


def _get_jump_clone_model():
    """Lazy import of memberaudit CharacterJumpClone to avoid import-time coupling."""

    from memberaudit.models import CharacterJumpClone  # pylint: disable=import-error,import-outside-toplevel

    return CharacterJumpClone


def _user_q(user) -> Q:
    """Return a Q filter scoping jump clones to a single user."""

    return Q(character__eve_character__character_ownership__user=user)


def _mains_only_q() -> Q:
    """Return a Q filter restricting to main characters only."""

    return Q(character__eve_character__userprofile__isnull=False)


class CharacterCloneImplantsFilter(BaseFilter):
    """Smart filter: does any jump clone of the user have the required implants?

    Requires ``memberaudit`` to be installed.

    The filter checks all jump clones of the user's characters (optionally
    restricted to mains).  A clone "passes" when:

    - ``require_all=True``  — the clone contains **all** of the listed implants.
    - ``require_all=False`` — the clone contains **at least one** of the listed
      implants.

    The first matching clone for any character makes the user pass.
    """

    implant_ids = models.TextField(
        help_text=_(
            "Type IDs of the required implants, one per line or comma-separated. "
            "Example: 9899, 9941 (you can look up type IDs on EVE SDE sites such as "
            "evesde.tech or via the in-game fitting/market browser)."
        ),
    )

    require_all = models.BooleanField(
        default=True,
        verbose_name=_("Require all implants"),
        help_text=_(
            "When enabled, a clone must have ALL listed implants to satisfy the "
            "filter. When disabled, having ANY one of the listed implants is enough."
        ),
    )

    include_alts = models.BooleanField(
        default=True,
        help_text=_(
            "When enabled, jump clones on all characters (including alts) are "
            "checked. Disable to restrict to main characters only."
        ),
    )

    class Meta:
        default_permissions = ()
        verbose_name = _("Character clone implants filter")
        verbose_name_plural = _("Character clone implants filters")

    def _required_ids(self) -> list:
        """Parse and return the list of required implant type IDs."""

        return _parse_ids(self.implant_ids)

    def _base_clone_qs(self, scope_q: Q) -> models.QuerySet:
        """Return a base jump-clone queryset scoped to the provided user filter."""

        JumpClone = _get_jump_clone_model()  # pylint: disable=invalid-name
        qs = JumpClone.objects.filter(scope_q)
        if not self.include_alts:
            qs = qs.filter(_mains_only_q())
        return qs

    def _clone_passes_all(self, clone_qs: models.QuerySet, required_ids: list) -> bool:
        """Return True if any clone in the queryset has ALL required implants."""

        return (
            clone_qs.annotate(
                matching_count=Count(
                    "implants",
                    filter=Q(implants__eve_type_id__in=required_ids),
                    distinct=True,
                )
            )
            .filter(matching_count=len(required_ids))
            .exists()
        )

    def _clone_passes_any(self, clone_qs: models.QuerySet, required_ids: list) -> bool:
        """Return True if any clone in the queryset has AT LEAST ONE required implant."""

        CharacterJumpCloneImplant = _get_memberaudit_jump_clone_implant_model()  # pylint: disable=invalid-name
        return CharacterJumpCloneImplant.objects.filter(
            jump_clone__in=clone_qs,
            eve_type_id__in=required_ids,
        ).exists()

    def process_filter(self, user: AbstractBaseUser) -> bool:
        """Return True if any of the user's jump clones satisfies the implant requirement."""

        required_ids = self._required_ids()
        if not required_ids:
            return False

        clone_qs = self._base_clone_qs(_user_q(user))

        if self.require_all:
            return self._clone_passes_all(clone_qs, required_ids)
        return self._clone_passes_any(clone_qs, required_ids)

    def _passing_clones_qs(self, base_qs: models.QuerySet, required_ids: list) -> models.QuerySet:
        """Return a queryset of jump clones that satisfy the implant requirement.

        Used by audit_filter to build the annotated/filtered clone set in one place,
        keeping audit_filter within the local-variable budget.
        """

        select = "character__eve_character__character_ownership__user"

        if self.require_all:
            return (
                base_qs.annotate(
                    matching_count=Count(
                        "implants",
                        filter=Q(implants__eve_type_id__in=required_ids),
                        distinct=True,
                    )
                )
                .filter(matching_count=len(required_ids))
                .select_related(select)
            )

        CharacterJumpCloneImplant = _get_memberaudit_jump_clone_implant_model()  # pylint: disable=invalid-name
        passing_ids = (
            CharacterJumpCloneImplant.objects.filter(
                jump_clone__in=base_qs,
                eve_type_id__in=required_ids,
            )
            .values_list("jump_clone_id", flat=True)
            .distinct()
        )
        return base_qs.filter(pk__in=passing_ids).select_related(select)

    def audit_filter(self, users: models.QuerySet) -> dict:
        """Return audit results for a queryset of users."""

        output = {user.pk: {"message": "", "check": False} for user in users}

        required_ids = self._required_ids()
        if not required_ids:
            return output

        user_ids = list(users.values_list("id", flat=True))
        scope_q = Q(character__eve_character__character_ownership__user_id__in=user_ids)
        passing_clones = self._passing_clones_qs(self._base_clone_qs(scope_q), required_ids)

        user_matches: dict = defaultdict(list)
        for clone in passing_clones:
            try:
                char_name = clone.character.eve_character.character_name
                user_id = clone.character.eve_character.character_ownership.user_id
                location_label = str(clone.location) if clone.location else str(_("Unknown location"))
            except AttributeError:
                continue
            user_matches[user_id].append(f"{char_name} ({location_label})")

        for user_id, entries in user_matches.items():
            output[user_id] = {
                "message": ", ".join(sorted(entries)),
                "check": True,
            }

        return output
