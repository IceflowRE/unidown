import unittest

from unidown import static_data
from unidown.core import updater


class UpdaterTest(unittest.TestCase):
    def test_get_newest_app_version(self):
        """
        Does not cover every possible option. As it only checks if it can be connect to Github.
        """
        try:
            updater.get_newest_app_version()
        except Exception:
            self.fail('Connection to Github failed.')

    def test_check_for_app_updates(self):
        static_data.VERSION = '1.0.0'
        try:
            self.assertTrue(updater.check_for_app_updates())
        except Exception:
            self.fail('Connection to Github failed.')
        static_data.VERSION = '100000.0.0'
        try:
            self.assertFalse(updater.check_for_app_updates())
        except Exception:
            self.fail('Connection to Github failed.')
