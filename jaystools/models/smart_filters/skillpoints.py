"""MemberAudit skill-point smart filters."""

from collections import defaultdict
from gettext import ngettext

import humanize
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseFilter
from .common import _get_memberaudit_character_model


class CharacterSkillPointFilter(BaseFilter):
    """Filter users by characters below a configured skillpoint threshold."""

    sp_threshold = models.PositiveBigIntegerField(
        help_text=_("The filter will work for character that has less than the amount specified")
    )

    ignore_alts = models.BooleanField(
        help_text="Ignore the alts and apply filter only to the main",
        default=False,
    )

    @property
    def name(self):
        """Build a dynamic display name based on the configured threshold."""

        sp_threshold = humanize.intword(self.sp_threshold)

        skill_point_threshold = ngettext(
            f"{sp_threshold} skill point",
            f"{sp_threshold} skill points",
            self.sp_threshold,
        )

        return _(f"Member Audit Skills Points [{skill_point_threshold}]")

    def process_filter(self, user: User) -> bool:
        character_model = _get_memberaudit_character_model()
        qs = character_model.objects.owned_by_user(user=user).filter(
            skillpoints__total__lte=self.sp_threshold
        )

        if self.ignore_alts:
            qs = qs.filter(eve_character__userprofile__isnull=False)

        return qs.exists()

    def audit_filter(self, users: models.QuerySet[User]) -> dict:
        character_model = _get_memberaudit_character_model()
        output = defaultdict(lambda: {"message": "", "check": False})

        for user in users:
            qs = character_model.objects.owned_by_user(user=user).filter(
                skillpoints__total__lte=self.sp_threshold
            )

            if self.ignore_alts:
                qs = qs.filter(eve_character__userprofile__isnull=False)

            if qs.count() > 0:
                chars = defaultdict(list)

                for char in qs:
                    chars[char.user.pk].append(char.eve_character.character_name)

                for char_user, char_list in chars.items():
                    output[char_user] = {
                        "message": ", ".join(sorted(char_list)),
                        "check": True,
                    }

        return output
