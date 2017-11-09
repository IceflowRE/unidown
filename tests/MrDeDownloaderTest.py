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
