from allianceauth import hooks

from .app_settings import securegroups_installed
from .app_settings import memberaudit_installed
from .models.smart_filters import RecruitmentFilter

if memberaudit_installed():
    from .models.smart_filters import CharacterSkillPointFilter


@hooks.register('discord_cogs_hook')
def register_cogs():
    return ["jaystools.cogs.me_recruter"]


if securegroups_installed():
    @hooks.register("secure_group_filters")
    def filters() -> list:
        """
        Secure group filter

        :return: Secure group filters
        :rtype: list
        """

        filter_list = [
            RecruitmentFilter
        ]

        if memberaudit_installed():
            filter_list.append(CharacterSkillPointFilter)

        return filter_list
