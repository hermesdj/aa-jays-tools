# Standard Library
import datetime
from collections import defaultdict
from gettext import ngettext

# Third Party
import humanize
# Alliance Auth
from allianceauth.hrapplications.models import Application
from allianceauth.services.hooks import get_extension_logger
# Django
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

# Local
from ..app_settings import memberaudit_installed

# MemberAudit
if memberaudit_installed():
    from memberaudit.models import (
        Character
    )

logger = get_extension_logger(__name__)


def _get_threshold_date(timedelta_in_days: int) -> datetime.datetime:
    """
    Get the threshold date

    :param timedelta_in_days: The timedelta in days
    :type timedelta_in_days: int
    :return: The threshold date
    :rtype: datetime.datetime
    """

    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=timedelta_in_days
    )


class BaseFilter(models.Model):
    """
    BaseFilter
    """

    name = models.CharField(
        max_length=500,
        help_text=_("The filter name that is shown to the admin.")
    )

    description = models.CharField(
        max_length=500,
        help_text=_("The filter description that is show to end users.")
    )

    class Meta:
        """
        Model meta definitions
        """
        abstract = True

    def __str__(self) -> str:
        """
        Model string representation
        :return:  The model string representation
        """
        return f"{self.name}: {self.description}"

    def process_filter(self, user: User) -> bool:
        """
        Process the filter
        :param user: the user
        :type user: User
        :return: return True when filter applies to the user, else False
        :rtype: bool
        """

        raise NotImplementedError(_("Please create a filter!"))

    def audit_filter(self, users: models.QuerySet[User]) -> dict:
        """
        Return information for each given user weather they pass the filter, and
        a help message shown in the audit feature.

        :param users: The users
        :type users: models.QuerySet[User]
        :return: The audit information
        :rtype: dict
        """

        raise NotImplementedError(_("Please create an audit function !"))


class RecruitmentFilter(BaseFilter):
    """
    RecruitmentFilter : used to check how many people the user has recruited over a period of time
    """

    days = models.IntegerField(
        default=30, help_text=_("The number of days to look back to count recruitments")
    )
    recruitments_needed = models.IntegerField(
        default=1, help_text=_("The number of recruitments to pass the filter")
    )

    class Meta:
        """
        Model meta definitions
        """

        verbose_name = _("Smart Filter: Number of recruitments in time period")
        verbose_name_plural = verbose_name

    def process_filter(self, user: User) -> bool:
        """
        Process the filter
        :param user:
        :return:
        """

        start_time = _get_threshold_date(timedelta_in_days=self.days)

        applications = Application.objects.filter(
            created__gte=start_time,
            reviewer_id=user.pk,
            approved=True
        )

        return applications.count() >= self.recruitments_needed

    def audit_filter(self, users: models.QuerySet[User]) -> dict:
        """
        Audit the users for the filter

        :param users:
        :return:
        """

        start_time = _get_threshold_date(timedelta_in_days=self.days)

        applications = Application.objects.filter(
            created__gte=start_time,
            reviewer_id__in=users.values_list("pk"),
            approved=True
        )

        users = defaultdict(list)
        for a in applications:
            users[a.reviewer_id].append(a.pk)

        output = defaultdict(lambda: {"message": 0, "check": False})

        for u, a_list in users.items():
            pass_fail = False

            if len(a_list) >= self.recruitments_needed:
                pass_fail = True

            output[u] = {"message": len(a_list), "check": pass_fail}

        return output


class CharacterSkillPointFilter(BaseFilter):
    sp_threshold = models.PositiveBigIntegerField(
        help_text=_("The filter will work for character that has less than the amount specified")
    )

    ignore_alts = models.BooleanField(
        help_text="Ignore the alts and apply filter only to the main",
        default=False
    )

    @property
    def name(self):
        sp_threshold = humanize.intword(self.sp_threshold)

        skill_point_threshold = ngettext(
            f"{sp_threshold} skill point",
            f"{sp_threshold} skill points",
            self.sp_threshold
        )

        return _(f"Member Audit Skills Points [{skill_point_threshold}]")

    def process_filter(self, user: User) -> bool:
        qs = Character.objects.owned_by_user(user=user).filter(skillpoints__total__lte=self.sp_threshold)

        if self.ignore_alts:
            qs = qs.filter(eve_character__userprofile__isnull=False)

        return qs.exists()

    def audit_filter(self, users: models.QuerySet[User]) -> dict:
        output = defaultdict(lambda: {"message": "", "check": False})

        for user in users:
            qs = Character.objects.owned_by_user(user=user).filter(
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
