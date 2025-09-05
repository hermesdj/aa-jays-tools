from allianceauth import hooks

from .app_settings import securegroups_installed
from .models import RecruitmentFilter


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

        return [
            RecruitmentFilter
        ]
