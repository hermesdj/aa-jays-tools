"""Tests for the FittingInHangarFilter smart filter."""

from unittest.mock import MagicMock, patch, PropertyMock

from django.test import TestCase

from jaystools.models.smart_filters.fitting import (
    FittingInHangarFilter,
    _CARGO_FLAGS,
    _ship_matches_fitting,
)


# ---------------------------------------------------------------------------
# Unit tests for the pure helpers
# ---------------------------------------------------------------------------

class TestShipMatchesFitting(TestCase):
    """Unit tests for the _ship_matches_fitting helper."""

    def _make_ship(self, children_items):
        """Build a mock ship asset with children items (type_id, location_flag)."""
        ship = MagicMock()
        children = []
        for type_id, flag in children_items:
            child = MagicMock()
            child.eve_type_id = type_id
            child.location_flag = flag
            children.append(child)
        ship.children.all.return_value = children
        return ship

    def test_empty_required_items_always_passes(self):
        """A bare hull with no required items should always match."""
        ship = self._make_ship([])
        self.assertTrue(_ship_matches_fitting(ship, []))

    def test_matching_ship_returns_true(self):
        """A ship that has all required modules should return True."""
        ship = self._make_ship([(1001, "HiSlot0"), (2002, "LoSlot0")])
        required = [(1001, "HiSlot0"), (2002, "LoSlot0")]
        self.assertTrue(_ship_matches_fitting(ship, required))

    def test_missing_module_returns_false(self):
        """A ship missing a required module should return False."""
        ship = self._make_ship([(1001, "HiSlot0")])
        required = [(1001, "HiSlot0"), (2002, "LoSlot0")]
        self.assertFalse(_ship_matches_fitting(ship, required))

    def test_wrong_slot_returns_false(self):
        """Same type_id in a different slot should not satisfy the requirement."""
        ship = self._make_ship([(1001, "HiSlot1")])
        required = [(1001, "HiSlot0")]
        self.assertFalse(_ship_matches_fitting(ship, required))

    def test_extra_modules_on_ship_still_passes(self):
        """Ship with more modules than required should still match."""
        ship = self._make_ship([(1001, "HiSlot0"), (2002, "LoSlot0"), (3003, "RigSlot0")])
        required = [(1001, "HiSlot0")]
        self.assertTrue(_ship_matches_fitting(ship, required))


class TestCargoFlags(TestCase):
    """Sanity checks on the _CARGO_FLAGS constant."""

    def test_cargo_flags_contains_expected_values(self):
        """Cargo, DroneBay and FighterBay must be in the ignored-flags set."""
        self.assertIn("Cargo", _CARGO_FLAGS)
        self.assertIn("DroneBay", _CARGO_FLAGS)
        self.assertIn("FighterBay", _CARGO_FLAGS)

    def test_module_slots_not_in_cargo_flags(self):
        """Module slots (HiSlot, LoSlot, MedSlot, RigSlot) must NOT be ignored."""
        for slot in ("HiSlot0", "LoSlot0", "MedSlot0", "RigSlot0"):
            self.assertNotIn(slot, _CARGO_FLAGS)


# ---------------------------------------------------------------------------
# Unit tests for FittingInHangarFilter model logic  (mocking DB)
# ---------------------------------------------------------------------------

class TestFittingInHangarFilterBuildRequiredItems(TestCase):
    """Tests for _build_required_items — the cargo-flag filtering logic."""

    def _make_fitting(self, items):
        """Build a mock Fitting with .items.values_list returning items."""
        fitting = MagicMock()
        fitting.items.values_list.return_value = items
        return fitting

    def test_all_items_returned_when_ignore_cargo_false(self):
        """With ignore_cargo=False all items including cargo should be returned."""
        filt = FittingInHangarFilter.__new__(FittingInHangarFilter)
        filt.ignore_cargo = False
        fitting = self._make_fitting([
            (1001, "HiSlot0"),
            (9999, "Cargo"),
        ])
        result = filt._build_required_items(fitting)
        self.assertEqual(set(result), {(1001, "HiSlot0"), (9999, "Cargo")})

    def test_cargo_items_removed_when_ignore_cargo_true(self):
        """With ignore_cargo=True cargo/drone/fighter bay items must be excluded."""
        filt = FittingInHangarFilter.__new__(FittingInHangarFilter)
        filt.ignore_cargo = True
        fitting = self._make_fitting([
            (1001, "HiSlot0"),
            (9999, "Cargo"),
            (8888, "DroneBay"),
            (7777, "FighterBay"),
        ])
        result = filt._build_required_items(fitting)
        self.assertEqual(result, [(1001, "HiSlot0")])

    def test_module_slots_never_removed(self):
        """Module slots should never be stripped regardless of the flag."""
        filt = FittingInHangarFilter.__new__(FittingInHangarFilter)
        filt.ignore_cargo = True
        fitting = self._make_fitting([
            (1001, "HiSlot0"),
            (2002, "LoSlot0"),
            (3003, "MedSlot0"),
            (4004, "RigSlot0"),
        ])
        result = filt._build_required_items(fitting)
        self.assertEqual(len(result), 4)


class TestFittingInHangarFilterProcessFilter(TestCase):
    """Tests for FittingInHangarFilter.process_filter using mocks."""

    def _make_filter(self, fitting_id=1, ignore_cargo=True, include_alts=True):
        filt = FittingInHangarFilter.__new__(FittingInHangarFilter)
        filt.fitting_id = fitting_id
        filt.ignore_cargo = ignore_cargo
        filt.include_alts = include_alts
        return filt

    def test_returns_false_when_fitting_not_found(self):
        """Should return False gracefully when the fitting ID does not exist."""
        filt = self._make_filter()

        with patch.object(FittingInHangarFilter, "_get_fitting", return_value=None), \
             patch.object(FittingInHangarFilter, "_candidate_ships", return_value=(None, None)):
            result = filt.process_filter(MagicMock())

        self.assertFalse(result)

    def test_returns_false_when_no_ships_match(self):
        """Should return False when the user owns no ships of the correct hull."""
        filt = self._make_filter()
        user = MagicMock()

        fitting = MagicMock()
        fitting.ship_type_type_id = 671
        fitting.items.values_list.return_value = [(1001, "HiSlot0")]

        empty_qs = MagicMock()
        empty_qs.filter.return_value = empty_qs
        empty_qs.prefetch_related.return_value = []

        with patch.object(FittingInHangarFilter, "_candidate_ships", return_value=(fitting, empty_qs)):
            result = filt.process_filter(user)

        self.assertFalse(result)

    def test_returns_true_when_matching_ship_found(self):
        """Should return True when a character owns a matching ship."""
        filt = self._make_filter(ignore_cargo=True)
        user = MagicMock()

        fitting = MagicMock()
        fitting.ship_type_type_id = 671
        fitting.items.values_list.return_value = [(1001, "HiSlot0")]

        child = MagicMock()
        child.eve_type_id = 1001
        child.location_flag = "HiSlot0"

        ship = MagicMock()
        ship.children.all.return_value = [child]

        ships_qs = MagicMock()
        ships_qs.filter.return_value = ships_qs
        ships_qs.prefetch_related.return_value = [ship]

        with patch.object(FittingInHangarFilter, "_candidate_ships", return_value=(fitting, ships_qs)):
            result = filt.process_filter(user)

        self.assertTrue(result)

