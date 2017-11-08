import unittest
from pathlib import Path

from unidown.core import updater


class UpdaterTest(unittest.TestCase):
    def test_get_newest_app_version(self):
        try:
            origin_version = updater.get_newest_app_version()
        except Exception:
            self.fail('Connection to Github failed.')
        with Path('./version').open(mode='r', encoding="utf8") as data_file:
            version = data_file.read()
        self.assertEqual(origin_version, version)
