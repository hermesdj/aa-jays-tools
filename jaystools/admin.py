from django.contrib import admin

from .app_settings import memberaudit_installed
from .app_settings import securegroups_installed
from .models.smart_filters import CharacterSkillPointFilter
from .models.smart_filters import RecruitmentFilter


class RecruitmentFilterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "days",
        "recruitments_needed"
    )

    select_related = True


class CharacterSkillPointFilterAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "sp_threshold",
        "ignore_alts"
    )

    select_related = True


if securegroups_installed():
    admin.site.register(RecruitmentFilter, RecruitmentFilterAdmin)

    if memberaudit_installed():
        admin.site.register(CharacterSkillPointFilter, CharacterSkillPointFilterAdmin)
