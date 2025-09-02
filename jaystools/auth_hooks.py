from allianceauth import hooks

@hooks.register('discord_cogs_hook')
def register_cogs():
    return ["jaystools.cogs.me_recruter"]