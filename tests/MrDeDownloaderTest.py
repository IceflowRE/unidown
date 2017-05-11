"""
Test for MrDeDownloader module.
"""
import unittest
import MrDeDownloader as Mdd


class TestMrDeDownloader(unittest.TestCase):
    """
    Tests for MrDeDownloader.
    """

    @classmethod
    def setUpClass(cls):
        Mdd.init()

    def test_app_update_check(self):
        """
        |MrDeDownloader| check for app updates:
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
