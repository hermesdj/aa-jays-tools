from django.conf import settings
from django.apps import apps

# List of ints to sync commands to non global commands
DISCORD_GUILD_IDS = getattr(settings, 'DISCORD_GUILD_IDS', [])

DISCORD_GUILD_ID = getattr(settings, 'DISCORD_GUILD_ID', None)

def get_all_servers():
    servers = []
    if DISCORD_GUILD_IDS:
        servers += DISCORD_GUILD_IDS
    if DISCORD_GUILD_ID and DISCORD_GUILD_ID not in servers:
        servers.append(int(DISCORD_GUILD_ID))
    return servers

def securegroups_installed() -> bool:
    """
    Check if the Alliance Auth Secure Groups module is installed

    :return:
    :rtype:
    """

    return apps.is_installed(app_name="securegroups")