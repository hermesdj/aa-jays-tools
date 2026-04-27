"""Settings helpers and optional app detection for jaystools."""

from typing import cast

from django.apps import apps
from django.conf import settings

# List of guild ids used to scope Discord commands.
DISCORD_GUILD_IDS = getattr(settings, "DISCORD_GUILD_IDS", [])

DISCORD_GUILD_ID = getattr(settings, "DISCORD_GUILD_ID", None)

MEMBERAUDIT_APP = "memberaudit"
SECUREGROUPS_APP = "securegroups"
HRAPPLICATIONS_APP = "allianceauth.hrapplications"


def get_all_servers():
    """Return a de-duplicated list of guild IDs for Discord command registration."""

    servers = []
    if DISCORD_GUILD_IDS:
        servers += DISCORD_GUILD_IDS
    if DISCORD_GUILD_ID is not None:
        guild_id = int(cast(str | int, DISCORD_GUILD_ID))
        if guild_id not in servers:
            servers.append(guild_id)
    return servers


def securegroups_installed() -> bool:
    """Return True when allianceauth-secure-groups is installed."""

    return apps.is_installed(SECUREGROUPS_APP)


def memberaudit_installed() -> bool:
    """Return True when aa-memberaudit is installed."""

    return apps.is_installed(MEMBERAUDIT_APP)


def hrapplications_installed() -> bool:
    """Return True when the Alliance Auth HR Applications app is installed."""

    return apps.is_installed(HRAPPLICATIONS_APP)


def get_memberaudit_character_model():
    """Return Member Audit Character model or raise when the app is unavailable."""

    if not memberaudit_installed():
        raise RuntimeError("memberaudit must be installed to use CharacterSkillPointFilter")

    from memberaudit.models import Character  # pylint: disable=import-error,import-outside-toplevel

    return Character


def get_memberaudit_jump_clone_model():
    """Return Member Audit CharacterJumpClone model or raise when unavailable."""

    if not memberaudit_installed():
        raise RuntimeError("memberaudit must be installed to use jump clone filters")

    from memberaudit.models import CharacterJumpClone  # pylint: disable=import-error,import-outside-toplevel

    return CharacterJumpClone


def get_hrapplications_application_model():
    """Return HR Applications Application model or raise when unavailable."""

    if not hrapplications_installed():
        raise RuntimeError("allianceauth.hrapplications must be installed to use RecruitmentFilter")

    from allianceauth.hrapplications.models import Application  # pylint: disable=import-outside-toplevel

    return Application
