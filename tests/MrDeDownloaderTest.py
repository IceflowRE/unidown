"""
Test for MrDeDownloader module.
"""
import unittest
from pathlib import Path

import MrDeDownloader as Mdd


class TestMrDeDownloader(unittest.TestCase):
    """
    Tests for MrDeDownloader.
    """

    @classmethod
    def setUpClass(cls):
        Mdd.init()

    def test_delete_dr_rec(self):
        """
        |MrDeDownloader| delete directories recursive.
        """
        Path("./testtemp/").mkdir()
        file = open("./testtemp/1", 'w')
        file.close()
        file = open("./testtemp/2", 'w')
        file.close()
        file = open("./testtemp/3", 'w')
        file.close()
        file = open("./testtemp/4", 'w')
        file.close()
        Path("./testtemp/temp/").mkdir()
        Path("./testtemp/temp2/").mkdir()
        file = open("./testtemp/temp/1", 'w')
        file.close()
        file = open("./testtemp/temp/2", 'w')
        file.close()
        file = open("./testtemp/temp/3", 'w')
        file.close()
        file = open("./testtemp/temp/4", 'w')
        file.close()
        Mdd.delete_dir_rec(Path("./testtemp/"))
        self.assertFalse(Path("./testtemp/").exists())

    def test_about(self):
        """
        |MrDeDownloader| about.
        """
        Mdd.about()

    def test_app_update_check(self):
        """
        |MrDeDownloader| check for app updates.
        """
        # check if github is up
        try:
            origin_version = Mdd.get_current_app_version()
        except Exception:
            self.fail('Connection to Github failed.')

        # check every position of the version tag each
        # version is older - update
        for i in range(0, 3):
            Mdd.VERSION = origin_version.copy()
            Mdd.VERSION[i] = str(int(origin_version[i]) - 1)
            with self.subTest(version=origin_version, test=Mdd.VERSION):
                self.assertTrue(Mdd.check_for_app_updates())

        # version is newer - no update
        for i in range(0, 3):
            Mdd.VERSION = origin_version.copy()
            Mdd.VERSION[i] = str(int(origin_version[i]) + 1)
            with self.subTest(version=origin_version, test=Mdd.VERSION):
                self.assertFalse(Mdd.check_for_app_updates())

        # version is equal - no update
        Mdd.VERSION = origin_version.copy()
        with self.subTest(version=origin_version, test=Mdd.VERSION):
            self.assertFalse(Mdd.check_for_app_updates())
