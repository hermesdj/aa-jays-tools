from django.contrib import admin

from .app_settings import securegroups_installed
from .models import RecruitmentFilter


class RecruitmentFilterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "days",
        "recruitments_needed"
    )

    select_related = True


if securegroups_installed():
    admin.site.register(RecruitmentFilter, RecruitmentFilterAdmin)
