"""Tests for the CharacterCloneImplantsFilter smart filter."""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from jaystools.models.smart_filters.clone_implants import (
    CharacterCloneImplantsFilter,
    _mains_only_q,
    _user_q,
)


# ---------------------------------------------------------------------------
# Unit tests for the Q helpers
# ---------------------------------------------------------------------------

class TestQHelpers(TestCase):
    """Smoke tests for Q-object helper functions."""

    def test_user_q_is_q_object(self):
        """_user_q should return a Django Q object."""
        from django.db.models import Q
        user = MagicMock()
        result = _user_q(user)
        self.assertIsInstance(result, Q)

    def test_mains_only_q_is_q_object(self):
        """_mains_only_q should return a Django Q object."""
        from django.db.models import Q
        result = _mains_only_q()
        self.assertIsInstance(result, Q)


# ---------------------------------------------------------------------------
# Unit tests for _required_ids parsing
# ---------------------------------------------------------------------------

class TestRequiredIdsParsing(TestCase):
    """Tests for _required_ids — wraps _parse_ids."""

    def _make_filter(self, implant_ids=""):
        filt = CharacterCloneImplantsFilter.__new__(CharacterCloneImplantsFilter)
        filt.implant_ids = implant_ids
        filt.require_all = True
        filt.include_alts = True
        return filt

    def test_empty_implant_ids_returns_empty_list(self):
        """Empty text field should yield an empty list."""
        filt = self._make_filter("")
        self.assertEqual(filt._required_ids(), [])

    def test_comma_separated_ids_parsed(self):
        """Comma-separated IDs should be parsed correctly."""
        filt = self._make_filter("9899, 9941")
        self.assertEqual(sorted(filt._required_ids()), [9899, 9941])

    def test_newline_separated_ids_parsed(self):
        """Newline-separated IDs should be parsed correctly."""
        filt = self._make_filter("9899\n9941\n10032")
        self.assertEqual(sorted(filt._required_ids()), [9899, 9941, 10032])

    def test_non_numeric_lines_are_ignored(self):
        """Non-numeric entries should be silently ignored."""
        filt = self._make_filter("9899\nbad_value\n9941")
        self.assertEqual(sorted(filt._required_ids()), [9899, 9941])


# ---------------------------------------------------------------------------
# Unit tests for process_filter
# ---------------------------------------------------------------------------

class TestProcessFilter(TestCase):
    """Tests for CharacterCloneImplantsFilter.process_filter."""

    def _make_filter(self, implant_ids="9899", require_all=True, include_alts=True):
        filt = CharacterCloneImplantsFilter.__new__(CharacterCloneImplantsFilter)
        filt.implant_ids = implant_ids
        filt.require_all = require_all
        filt.include_alts = include_alts
        return filt

    def _make_clone_qs(self, clone_count_match=0, has_implant=False):
        """Build a mock queryset simulating the jump clone ORM chain."""
        qs = MagicMock()
        qs.filter.return_value = qs
        qs.annotate.return_value = qs
        # exists() on the annotated+filtered queryset
        qs.exists.return_value = clone_count_match > 0 or has_implant
        return qs

    def test_returns_false_when_no_implant_ids_configured(self):
        """Should return False immediately when no implant IDs are configured."""
        filt = self._make_filter(implant_ids="")
        result = filt.process_filter(MagicMock())
        self.assertFalse(result)

    def test_require_all_returns_true_when_clone_has_all_implants(self):
        """With require_all=True, returns True when a clone has all required implants."""
        filt = self._make_filter(implant_ids="9899\n9941", require_all=True)
        user = MagicMock()

        clone_qs = self._make_clone_qs(clone_count_match=1)

        with patch.object(CharacterCloneImplantsFilter, "_base_clone_qs", return_value=clone_qs):
            result = filt.process_filter(user)

        self.assertTrue(result)

    def test_require_all_returns_false_when_no_clone_has_all_implants(self):
        """With require_all=True, returns False when no clone has all required implants."""
        filt = self._make_filter(implant_ids="9899\n9941", require_all=True)
        user = MagicMock()

        clone_qs = self._make_clone_qs(clone_count_match=0)

        with patch.object(CharacterCloneImplantsFilter, "_base_clone_qs", return_value=clone_qs):
            result = filt.process_filter(user)

        self.assertFalse(result)

    def test_require_any_returns_true_when_any_implant_present(self):
        """With require_all=False, returns True when any clone has any required implant."""
        filt = self._make_filter(implant_ids="9899", require_all=False)
        user = MagicMock()

        clone_qs = MagicMock()
        clone_qs.filter.return_value = clone_qs

        implant_qs = MagicMock()
        implant_qs.filter.return_value = implant_qs
        implant_qs.exists.return_value = True

        with patch.object(CharacterCloneImplantsFilter, "_base_clone_qs", return_value=clone_qs), \
             patch(
                 "jaystools.models.smart_filters.clone_implants._get_memberaudit_jump_clone_implant_model",
                 return_value=MagicMock(**{"objects.filter.return_value": implant_qs}),
             ):
            result = filt.process_filter(user)

        self.assertTrue(result)

    def test_require_any_returns_false_when_no_implant_present(self):
        """With require_all=False, returns False when no matching implant exists."""
        filt = self._make_filter(implant_ids="9899", require_all=False)
        user = MagicMock()

        clone_qs = MagicMock()
        clone_qs.filter.return_value = clone_qs

        implant_qs = MagicMock()
        implant_qs.filter.return_value = implant_qs
        implant_qs.exists.return_value = False

        with patch.object(CharacterCloneImplantsFilter, "_base_clone_qs", return_value=clone_qs), \
             patch(
                 "jaystools.models.smart_filters.clone_implants._get_memberaudit_jump_clone_implant_model",
                 return_value=MagicMock(**{"objects.filter.return_value": implant_qs}),
             ):
            result = filt.process_filter(user)

        self.assertFalse(result)


# ---------------------------------------------------------------------------
# Unit tests for audit_filter
# ---------------------------------------------------------------------------

class TestAuditFilter(TestCase):
    """Tests for CharacterCloneImplantsFilter.audit_filter."""

    def _make_filter(self, implant_ids="9899", require_all=True, include_alts=True):
        filt = CharacterCloneImplantsFilter.__new__(CharacterCloneImplantsFilter)
        filt.implant_ids = implant_ids
        filt.require_all = require_all
        filt.include_alts = include_alts
        return filt

    def _make_users(self, *pks):
        """Build a mock queryset of users."""
        qs = MagicMock()
        qs.__iter__ = MagicMock(return_value=iter([MagicMock(pk=pk) for pk in pks]))
        qs.values_list.return_value = list(pks)
        return qs

    def test_empty_implant_ids_returns_all_check_false(self):
        """Empty implant_ids should result in all users getting check=False."""
        filt = self._make_filter(implant_ids="")
        users = self._make_users(1, 2)
        result = filt.audit_filter(users)
        self.assertFalse(result[1]["check"])
        self.assertFalse(result[2]["check"])

    def test_audit_marks_matching_user(self):
        """Users with matching clones should have check=True and a message."""
        filt = self._make_filter(implant_ids="9899", require_all=True)

        user1 = MagicMock(pk=1)
        user2 = MagicMock(pk=2)
        users_qs = MagicMock()
        users_qs.__iter__ = MagicMock(return_value=iter([user1, user2]))
        users_qs.values_list.return_value = [1, 2]

        # Build a mock passing clone for user1
        clone = MagicMock()
        clone.character.eve_character.character_name = "TestPilot"
        clone.character.eve_character.character_ownership.user_id = 1
        clone.location.__str__ = MagicMock(return_value="Jita IV")

        passing_qs = [clone]

        with patch.object(CharacterCloneImplantsFilter, "_base_clone_qs", return_value=MagicMock()), \
             patch.object(CharacterCloneImplantsFilter, "_passing_clones_qs", return_value=passing_qs):
            result = filt.audit_filter(users_qs)

        self.assertTrue(result[1]["check"])
        self.assertIn("TestPilot", result[1]["message"])
        self.assertFalse(result[2]["check"])


