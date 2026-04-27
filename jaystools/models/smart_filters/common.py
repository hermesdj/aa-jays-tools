"""Shared helpers for jaystools smart filters."""

import datetime

from ...app_settings import get_memberaudit_character_model
from ...app_settings import get_memberaudit_jump_clone_model


def _get_memberaudit_character_model():
    """Compatibility wrapper around app_settings lazy model resolver."""

    return get_memberaudit_character_model()


def _get_memberaudit_jump_clone_model():
    """Compatibility wrapper around app_settings lazy model resolver."""

    return get_memberaudit_jump_clone_model()


def _parse_ids(raw: str) -> list:
    """Parse newline/comma-separated integer IDs from a raw text field."""

    result = []
    for part in raw.replace(",", "\n").splitlines():
        part = part.strip()
        if part.isdigit():
            result.append(int(part))
    return result


def _get_threshold_date(timedelta_in_days: int) -> datetime.datetime:
    """Return UTC now minus the specified number of days."""

    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=timedelta_in_days
    )
