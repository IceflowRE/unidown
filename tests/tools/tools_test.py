import unittest
from pathlib import Path

from unidown.tools import delete_dir_rec


class ToolsTest(unittest.TestCase):
    def test_delete_dir_rec(self):
        Path("./test_delete_dir_rec/").mkdir()
        for number in range(1, 4):
            file = open("./test_delete_dir_rec/" + str(number), 'w')
            file.close()
        Path("./test_delete_dir_rec/temp/").mkdir()
        for number in range(1, 4):
            file = open("./test_delete_dir_rec/temp/" + str(number), 'w')
            file.close()
        Path("./test_delete_dir_rec/temp2/").mkdir()
        delete_dir_rec(Path("./test_delete_dir_rec/"))

        self.assertFalse(Path("./test_delete_dir_rec/").exists())

        self.assertFalse(Path("./donotexist/").exists())
        delete_dir_rec(Path("./donotexist/"))
        self.assertFalse(Path("./donotexist/").exists())
