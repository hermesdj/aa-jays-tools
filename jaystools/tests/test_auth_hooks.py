from django.test import SimpleTestCase

from jaystools import auth_hooks


class TestAuthHooks(SimpleTestCase):
    def test_register_cogs_contains_expected_cog_module(self):
        self.assertEqual(auth_hooks.register_cogs(), ["jaystools.cogs.me_recruter"])

    def test_secure_group_filters_hook_not_registered_without_securegroups(self):
        self.assertFalse(hasattr(auth_hooks, "filters"))

