"""Fittings + MemberAudit hangar smart filter for jaystools."""

from collections import defaultdict

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BaseFilter
from .common import _get_fittings_fitting_model
from .common import _get_memberaudit_character_asset_model

# Flags in FittingItem that correspond to consumables / cargo bays.
# When ignore_cargo is True, these are excluded from the match check so a ship
# with partially-stocked bays or different ammo still passes the filter.
_CARGO_FLAGS = frozenset({"Cargo", "DroneBay", "FighterBay"})


def _ship_matches_fitting(ship_asset, required_items: list[tuple[int, str]]) -> bool:
    """Return True if ship_asset has all required (type_id, slot_flag) pairs fitted.

    Args:
        ship_asset: A memberaudit CharacterAsset instance representing a ship.
        required_items: List of (type_id, location_flag) tuples from the fitting,
            potentially already filtered for cargo exclusion.

    Returns:
        True when every required (type_id, flag) pair is present among the ship's
        children assets.
    """

    if not required_items:
        # A fitting with no required items (e.g. bare hull) is always satisfied.
        return True

    child_signatures = {
        (child.eve_type_id, child.location_flag)
        for child in ship_asset.children.all()
    }

    return all(pair in child_signatures for pair in required_items)


class FittingInHangarFilter(BaseFilter):
    """Smart filter: does the user own a ship matching a specific fitting?

    Requires both the `fittings` plugin and `memberaudit` to be installed.
    A character "has the fitting" when they own a singleton ship of the correct
    hull type with all required module slots filled according to the chosen
    fitting definition.

    The `ignore_cargo` option lets you skip cargo / drone bay / fighter bay
    items from the check — useful for doctrines where ammo and consumable
    loadouts vary or are not tracked.
    """

    fitting_id = models.PositiveBigIntegerField(
        help_text=_("ID of the fitting to check (from the Fittings plugin)."),
    )

    ignore_cargo = models.BooleanField(
        default=True,
        verbose_name=_("Ignore cargo / ammo"),
        help_text=_(
            "When enabled, Cargo, DroneBay and FighterBay items are excluded from "
            "the check. The ship hull and fitted modules still need to match, but "
            "the hold contents are ignored. Recommended for doctrine compliance "
            "checks where pilots will have consumed ammo or adjusted their drones."
        ),
    )

    include_alts = models.BooleanField(
        default=True,
        help_text=_(
            "When enabled, alts are included in the asset check. "
            "Disable to restrict to main characters only."
        ),
    )

    class Meta:
        default_permissions = ()
        verbose_name = _("Fitting in hangar filter")
        verbose_name_plural = _("Fitting in hangar filters")

    def _get_fitting(self):
        """Return the Fitting instance for the configured fitting_id."""

        fitting_model = _get_fittings_fitting_model()
        try:
            return fitting_model.objects.get(pk=self.fitting_id)
        except fitting_model.DoesNotExist:
            return None

    def _build_required_items(self, fitting) -> list[tuple[int, str]]:
        """Build the list of (type_id, flag) pairs required by the fitting.

        If ignore_cargo is True, Cargo / DroneBay / FighterBay items are omitted
        so that only hull modules (hi/med/lo/rig/sub-system/service slots) are
        verified.
        """

        items = list(fitting.items.values_list("type_id", "flag"))
        if self.ignore_cargo:
            items = [(t, f) for t, f in items if f not in _CARGO_FLAGS]
        return items

    def _candidate_ships(self, users_filter: models.Q):
        """Return a queryset of singleton ship assets matching the fitting hull for the given user filter."""

        fitting = self._get_fitting()
        if fitting is None:
            return None, None

        CharacterAsset = _get_memberaudit_character_asset_model()  # pylint: disable=invalid-name
        ships = CharacterAsset.objects.filter(
            users_filter,
            eve_type_id=fitting.ship_type_type_id,
            is_singleton=True,
        )
        return fitting, ships

    def process_filter(self, user: AbstractBaseUser) -> bool:
        """Return True if the user owns at least one character with the fitting in their hangar."""

        user_q = models.Q(character__eve_character__character_ownership__user=user)
        fitting, ships = self._candidate_ships(user_q)
        if fitting is None:
            return False

        if not self.include_alts:
            ships = ships.filter(character__eve_character__userprofile__isnull=False)

        required_items = self._build_required_items(fitting)

        for ship in ships.prefetch_related("children"):
            if _ship_matches_fitting(ship, required_items):
                return True

        return False

    def audit_filter(self, users: models.QuerySet) -> dict:
        """Return audit results for a queryset of users."""

        output = {
            user.pk: {"message": "", "check": False}
            for user in users
        }

        user_ids = list(users.values_list("id", flat=True))
        user_q = models.Q(character__eve_character__character_ownership__user_id__in=user_ids)
        fitting, ships = self._candidate_ships(user_q)
        if fitting is None:
            return output

        if not self.include_alts:
            ships = ships.filter(character__eve_character__userprofile__isnull=False)

        required_items = self._build_required_items(fitting)

        # Annotate each ship with its owner's user_id and character name for reporting.
        ships_with_owner = ships.prefetch_related("children").select_related(
            "character__eve_character__character_ownership__user",
            "character__eve_character",
        )

        user_matches: dict = defaultdict(list)
        for ship in ships_with_owner:
            if not _ship_matches_fitting(ship, required_items):
                continue

            try:
                char_name = ship.character.eve_character.character_name
                user_id = ship.character.eve_character.character_ownership.user_id
            except AttributeError:
                continue

            user_matches[user_id].append(char_name)

        for user_id, char_names in user_matches.items():
            output[user_id] = {
                "message": ", ".join(sorted(char_names)),
                "check": True,
            }

        return output
