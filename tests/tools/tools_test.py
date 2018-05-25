import unittest
from pathlib import Path

from unidown.tools import delete_dir_rec


class ToolsTest(unittest.TestCase):
    def test_delete_dir_rec(self):
        Path("./testtemp/").mkdir()
        for number in range(1, 4):
            file = open("./testtemp/" + str(number), 'w')
            file.close()
        Path("./testtemp/temp/").mkdir()
        for number in range(1, 4):
            file = open("./testtemp/temp/" + str(number), 'w')
            file.close()
        Path("./testtemp/temp2/").mkdir()
        delete_dir_rec(Path("./testtemp/"))

        self.assertFalse(Path("./testtemp/").exists())

        self.assertFalse(Path("./donotexist/").exists())
        delete_dir_rec(Path("./donotexist/"))
        self.assertFalse(Path("./donotexist/").exists())
