"""Admin registrations for jaystools smart filters."""

from django.contrib import admin

from .app_settings import memberaudit_installed
from .app_settings import securegroups_installed
from .models.smart_filters import JumpCloneConstellationFilter
from .models.smart_filters import JumpCloneRegionFilter
from .models.smart_filters import JumpCloneSolarSystemFilter
from .models.smart_filters import JumpCloneStationFilter
from .models.smart_filters import RecruitmentFilter

if memberaudit_installed():
    from .models.smart_filters import CharacterSkillPointFilter


class RecruitmentFilterAdmin(admin.ModelAdmin):
    """Admin configuration for recruitment-based smart filters."""

    list_display = (
        "name",
        "description",
        "days",
        "recruitments_needed"
    )

    select_related = True


class CharacterSkillPointFilterAdmin(admin.ModelAdmin):
    """Admin configuration for member-audit skillpoint filters."""

    list_display = (
        "name",
        "description",
        "sp_threshold",
        "ignore_alts"
    )

    select_related = True


class JumpCloneStationFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone station filters."""

    list_display = ("name", "description", "include_alts")


class JumpCloneSolarSystemFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone solar system filters."""

    list_display = ("name", "description", "include_alts")


class JumpCloneConstellationFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone constellation filters."""

    list_display = ("name", "description", "include_alts")


class JumpCloneRegionFilterAdmin(admin.ModelAdmin):
    """Admin configuration for jump clone region filters."""

    list_display = ("name", "description", "include_alts")


if securegroups_installed():
    admin.site.register(RecruitmentFilter, RecruitmentFilterAdmin)
    admin.site.register(JumpCloneStationFilter, JumpCloneStationFilterAdmin)
    admin.site.register(JumpCloneSolarSystemFilter, JumpCloneSolarSystemFilterAdmin)
    admin.site.register(JumpCloneConstellationFilter, JumpCloneConstellationFilterAdmin)
    admin.site.register(JumpCloneRegionFilter, JumpCloneRegionFilterAdmin)

    if memberaudit_installed():
        admin.site.register(CharacterSkillPointFilter, CharacterSkillPointFilterAdmin)
