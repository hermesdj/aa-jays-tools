"""Recruitment-related smart filters."""

from collections import defaultdict

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from ...app_settings import get_hrapplications_application_model
from .base import BaseFilter
from .common import _get_threshold_date


class RecruitmentFilter(BaseFilter):
    """Check if user approved a minimum number of recruitments in a time window."""

    days = models.IntegerField(
        default=30, help_text=_("The number of days to look back to count recruitments")
    )
    recruitments_needed = models.IntegerField(
        default=1, help_text=_("The number of recruitments to pass the filter")
    )

    class Meta:
        """Model meta for recruitment count filter."""

        verbose_name = _("Smart Filter: Number of recruitments in time period")
        verbose_name_plural = verbose_name

    def process_filter(self, user: AbstractBaseUser) -> bool:
        start_time = _get_threshold_date(timedelta_in_days=self.days)
        application_model = get_hrapplications_application_model()

        applications = application_model.objects.filter(
            created__gte=start_time,
            reviewer_id=user.pk,
            approved=True,
        )

        return applications.count() >= self.recruitments_needed

    def audit_filter(self, users: models.QuerySet) -> dict:
        start_time = _get_threshold_date(timedelta_in_days=self.days)
        application_model = get_hrapplications_application_model()

        applications = application_model.objects.filter(
            created__gte=start_time,
            reviewer_id__in=users.values_list("pk"),
            approved=True,
        )

        users_matches = defaultdict(list)
        for application in applications:
            users_matches[application.reviewer_id].append(application.pk)

        output = defaultdict(lambda: {"message": 0, "check": False})

        for user_id, app_ids in users_matches.items():
            output[user_id] = {
                "message": len(app_ids),
                "check": len(app_ids) >= self.recruitments_needed,
            }

        return output
