import unittest

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
