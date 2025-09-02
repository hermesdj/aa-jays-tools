from django.conf import settings

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