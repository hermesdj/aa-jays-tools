import datetime
from collections import defaultdict

from allianceauth.hrapplications.models import Application
from allianceauth.services.hooks import get_extension_logger
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

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
