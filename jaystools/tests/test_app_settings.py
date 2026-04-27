from unittest.mock import patch

from django.test import SimpleTestCase

from jaystools import app_settings


class TestAppSettings(SimpleTestCase):
    def test_get_all_servers_merges_and_deduplicates(self):
        with patch.object(app_settings, "DISCORD_GUILD_IDS", [11, 22]):
            with patch.object(app_settings, "DISCORD_GUILD_ID", "22"):
                self.assertEqual(app_settings.get_all_servers(), [11, 22])

    def test_get_all_servers_appends_single_guild_id(self):
        with patch.object(app_settings, "DISCORD_GUILD_IDS", []):
            with patch.object(app_settings, "DISCORD_GUILD_ID", "33"):
                self.assertEqual(app_settings.get_all_servers(), [33])

    def test_securegroups_installed_checks_expected_app_label(self):
        with patch("jaystools.app_settings.apps.is_installed", return_value=True) as mocked_call:
            self.assertTrue(app_settings.securegroups_installed())
            mocked_call.assert_called_once_with("securegroups")

    def test_memberaudit_installed_checks_expected_app_label(self):
        with patch("jaystools.app_settings.apps.is_installed", return_value=True) as mocked_call:
            self.assertTrue(app_settings.memberaudit_installed())
            mocked_call.assert_called_once_with("memberaudit")

    def test_hrapplications_installed_checks_expected_app_name(self):
        with patch("jaystools.app_settings.apps.is_installed", return_value=True) as mocked_call:
            self.assertTrue(app_settings.hrapplications_installed())
            mocked_call.assert_called_once_with("allianceauth.hrapplications")

    def test_get_hrapplications_application_model_raises_when_missing(self):
        with patch("jaystools.app_settings.hrapplications_installed", return_value=False):
            with self.assertRaises(RuntimeError):
                app_settings.get_hrapplications_application_model()

    def test_get_memberaudit_character_model_raises_when_missing(self):
        with patch("jaystools.app_settings.memberaudit_installed", return_value=False):
            with self.assertRaises(RuntimeError):
                app_settings.get_memberaudit_character_model()

    def test_get_memberaudit_jump_clone_model_raises_when_missing(self):
        with patch("jaystools.app_settings.memberaudit_installed", return_value=False):
            with self.assertRaises(RuntimeError):
                app_settings.get_memberaudit_jump_clone_model()

