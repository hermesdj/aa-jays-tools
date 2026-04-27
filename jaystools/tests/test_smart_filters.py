import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase

from jaystools.models.smart_filters import BaseFilter
from jaystools.models.smart_filters import CharacterSkillPointFilter
from jaystools.models.smart_filters import JumpCloneConstellationFilter
from jaystools.models.smart_filters import JumpCloneRegionFilter
from jaystools.models.smart_filters import JumpCloneSolarSystemFilter
from jaystools.models.smart_filters import JumpCloneStationFilter
from jaystools.models.smart_filters import RecruitmentFilter
from jaystools.models.smart_filters import _get_threshold_date
from jaystools.models.smart_filters import _parse_ids


class DummyFilter(BaseFilter):
    """Concrete filter used to test BaseFilter contract."""

    class Meta:
        app_label = "jaystools"


class TestSmartFilters(SimpleTestCase):
    def test_threshold_date_uses_timezone_aware_utc_datetime(self):
        days = 10
        actual = _get_threshold_date(timedelta_in_days=days)
        expected = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)

        self.assertIsNotNone(actual.tzinfo)
        self.assertLess(abs((actual - expected).total_seconds()), 2)

    def test_base_filter_contract_methods_raise_when_not_implemented(self):
        filter_obj = DummyFilter(name="Dummy", description="Dummy")

        with self.assertRaises(NotImplementedError):
            filter_obj.process_filter(User(pk=1))

        with self.assertRaises(NotImplementedError):
            filter_obj.audit_filter(MagicMock())

    def test_recruitment_filter_passes_when_minimum_count_is_reached(self):
        filter_obj = RecruitmentFilter(days=30, recruitments_needed=2)
        application_model = MagicMock()
        application_model.objects.filter.return_value.count.return_value = 2

        with patch(
            "jaystools.models.smart_filters.recruitment.get_hrapplications_application_model",
            return_value=application_model,
        ):
            self.assertTrue(filter_obj.process_filter(User(pk=42)))
            application_model.objects.filter.assert_called_once()

    def test_recruitment_filter_audit_builds_expected_output(self):
        filter_obj = RecruitmentFilter(days=30, recruitments_needed=2)
        applications = [
            SimpleNamespace(reviewer_id=1, pk=10),
            SimpleNamespace(reviewer_id=1, pk=11),
            SimpleNamespace(reviewer_id=2, pk=20),
        ]

        users = MagicMock()
        users.values_list.return_value = [1, 2]

        application_model = MagicMock()
        application_model.objects.filter.return_value = applications

        with patch(
            "jaystools.models.smart_filters.recruitment.get_hrapplications_application_model",
            return_value=application_model,
        ):
            result = filter_obj.audit_filter(users)

        self.assertEqual(result[1], {"message": 2, "check": True})
        self.assertEqual(result[2], {"message": 1, "check": False})

    def test_character_skill_point_filter_name_uses_threshold(self):
        filter_obj = CharacterSkillPointFilter(description="Skill point gate", sp_threshold=2000000)

        self.assertIn("Member Audit Skills Points", str(filter_obj.name))


class TestParseIds(SimpleTestCase):
    def test_newline_separated_ids_are_parsed(self):
        self.assertEqual(_parse_ids("10\n20\n30"), [10, 20, 30])

    def test_comma_separated_ids_are_parsed(self):
        self.assertEqual(_parse_ids("10,20,30"), [10, 20, 30])

    def test_blank_lines_are_ignored(self):
        self.assertEqual(_parse_ids("10\n\n20\n"), [10, 20])

    def test_non_numeric_entries_are_ignored(self):
        self.assertEqual(_parse_ids("10\nabc\n20"), [10, 20])

    def test_empty_string_returns_empty_list(self):
        self.assertEqual(_parse_ids(""), [])


class TestJumpCloneStationFilter(SimpleTestCase):
    def _make_filter(self, ids="60003760\n60004588", include_alts=True):
        f = JumpCloneStationFilter(
            description="desc",
            location_ids=ids,
            include_alts=include_alts,
        )
        return f

    def test_configured_ids_are_parsed_correctly(self):
        f = self._make_filter("60003760\n60004588")
        self.assertEqual(f._get_configured_ids(), [60003760, 60004588])

    def test_queryset_kwargs_use_location_id_path(self):
        f = self._make_filter("60003760")
        kwargs = f._location_queryset_kwargs([60003760])
        self.assertIn("location__id__in", kwargs)

    def test_process_filter_returns_true_when_clone_found(self):
        f = self._make_filter("60003760")
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = True

        with patch("jaystools.models.smart_filters.base._get_memberaudit_jump_clone_model") as mock_model:
            mock_model.return_value.objects.filter.return_value = mock_qs
            self.assertTrue(f.process_filter(User(pk=1)))

    def test_process_filter_returns_false_when_no_ids_configured(self):
        f = self._make_filter("")
        self.assertFalse(f.process_filter(User(pk=1)))

    def test_process_filter_restricts_to_mains_when_include_alts_false(self):
        f = self._make_filter("60003760", include_alts=False)
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.exists.return_value = False

        with patch("jaystools.models.smart_filters.base._get_memberaudit_jump_clone_model") as mock_model:
            mock_model.return_value.objects.filter.return_value = mock_qs
            f.process_filter(User(pk=1))
            # first filter = location kwargs, second filter = userprofile (mains only)
            self.assertEqual(mock_qs.filter.call_count, 1)

    def test_audit_filter_returns_false_check_when_no_ids(self):
        f = self._make_filter("")
        users = MagicMock()
        users.values_list.return_value = [1, 2]
        result = f.audit_filter(users)
        self.assertFalse(result[1]["check"])
        self.assertFalse(result[2]["check"])

    def test_audit_filter_builds_matching_output(self):
        f = self._make_filter("60003760")
        users = MagicMock()
        users.values_list.return_value = [42]

        rows = [{"user_id": 42, "character_name": "Alpha", "location_name": "Jita IV - Moon 4"}]
        mock_qs = MagicMock()
        mock_qs.filter.return_value = mock_qs
        mock_qs.values.return_value.distinct.return_value = rows

        with patch("jaystools.models.smart_filters.base._get_memberaudit_jump_clone_model") as mock_model:
            mock_model.return_value.objects.filter.return_value = mock_qs
            result = f.audit_filter(users)

        self.assertTrue(result[42]["check"])
        self.assertIn("Alpha", result[42]["message"])


class TestJumpCloneSolarSystemFilter(SimpleTestCase):
    def test_configured_ids_are_parsed_correctly(self):
        f = JumpCloneSolarSystemFilter(
            description="d", solar_system_ids="30000142\n30002187", include_alts=True
        )
        self.assertEqual(f._get_configured_ids(), [30000142, 30002187])

    def test_location_queryset_kwargs_use_solar_system_path(self):
        f = JumpCloneSolarSystemFilter(
            description="d", solar_system_ids="30000142", include_alts=True
        )
        kwargs = f._location_queryset_kwargs([30000142])
        self.assertIn("location__eve_solar_system__id__in", kwargs)
        self.assertEqual(kwargs["location__eve_solar_system__id__in"], [30000142])


class TestJumpCloneConstellationFilter(SimpleTestCase):
    def test_location_queryset_kwargs_use_constellation_path(self):
        f = JumpCloneConstellationFilter(
            description="d", constellation_ids="20000020", include_alts=True
        )
        kwargs = f._location_queryset_kwargs([20000020])
        self.assertIn("location__eve_solar_system__eve_constellation__id__in", kwargs)

    def test_configured_ids_are_parsed_correctly(self):
        f = JumpCloneConstellationFilter(
            description="d", constellation_ids="20000020\n20000021", include_alts=True
        )
        self.assertEqual(f._get_configured_ids(), [20000020, 20000021])


class TestJumpCloneRegionFilter(SimpleTestCase):
    def test_location_queryset_kwargs_use_region_path(self):
        f = JumpCloneRegionFilter(
            description="d", region_ids="10000002", include_alts=True
        )
        kwargs = f._location_queryset_kwargs([10000002])
        self.assertIn("location__eve_solar_system__eve_constellation__eve_region__id__in", kwargs)

    def test_configured_ids_are_parsed_correctly(self):
        f = JumpCloneRegionFilter(
            description="d", region_ids="10000002", include_alts=True
        )
        self.assertEqual(f._get_configured_ids(), [10000002])


