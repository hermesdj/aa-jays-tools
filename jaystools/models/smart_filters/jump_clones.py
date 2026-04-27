"""Jump clone location smart filters."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import _JumpCloneBaseFilter
from .common import _parse_ids


class JumpCloneStationFilter(_JumpCloneBaseFilter):
    """Filter users by jump clones in specific stations/structures."""

    location_ids = models.TextField(
        help_text=_(
            "One station or structure ID per line (or comma-separated). "
            "The filter passes if a character has a jump clone in any of these locations."
        )
    )

    class Meta:
        """Model meta for jump clone station/structure filter."""

        verbose_name = _("Smart Filter: Jump Clone in Station/Structure")
        verbose_name_plural = verbose_name

    def _get_configured_ids(self) -> list:
        return _parse_ids(self.location_ids)

    def _location_queryset_kwargs(self, ids: list) -> dict:
        return {"location__id__in": ids}


class JumpCloneSolarSystemFilter(_JumpCloneBaseFilter):
    """Filter users by jump clones in specific solar systems."""

    solar_system_ids = models.TextField(
        help_text=_(
            "One solar system ID per line (or comma-separated). "
            "The filter passes if a character has a jump clone in any of these solar systems."
        )
    )

    class Meta:
        """Model meta for jump clone solar system filter."""

        verbose_name = _("Smart Filter: Jump Clone in Solar System")
        verbose_name_plural = verbose_name

    def _get_configured_ids(self) -> list:
        return _parse_ids(self.solar_system_ids)

    def _location_queryset_kwargs(self, ids: list) -> dict:
        return {"location__eve_solar_system__id__in": ids}


class JumpCloneConstellationFilter(_JumpCloneBaseFilter):
    """Filter users by jump clones in specific constellations."""

    constellation_ids = models.TextField(
        help_text=_(
            "One constellation ID per line (or comma-separated). "
            "The filter passes if a character has a jump clone anywhere in these constellations."
        )
    )

    class Meta:
        """Model meta for jump clone constellation filter."""

        verbose_name = _("Smart Filter: Jump Clone in Constellation")
        verbose_name_plural = verbose_name

    def _get_configured_ids(self) -> list:
        return _parse_ids(self.constellation_ids)

    def _location_queryset_kwargs(self, ids: list) -> dict:
        return {"location__eve_solar_system__eve_constellation__id__in": ids}


class JumpCloneRegionFilter(_JumpCloneBaseFilter):
    """Filter users by jump clones in specific regions."""

    region_ids = models.TextField(
        help_text=_(
            "One region ID per line (or comma-separated). "
            "The filter passes if a character has a jump clone anywhere in these regions."
        )
    )

    class Meta:
        """Model meta for jump clone region filter."""

        verbose_name = _("Smart Filter: Jump Clone in Region")
        verbose_name_plural = verbose_name

    def _get_configured_ids(self) -> list:
        return _parse_ids(self.region_ids)

    def _location_queryset_kwargs(self, ids: list) -> dict:
        return {"location__eve_solar_system__eve_constellation__eve_region__id__in": ids}
