import unittest
from pathlib import Path

from unidown.tools import unlink_dir_rec


class ToolsTest(unittest.TestCase):
    def test_delete_dir_rec(self):
        folder = Path("./test-tmp/test_delete_dir_rec/")
        folder.mkdir(parents=True, exist_ok=True)
        for number in range(1, 4):
            with folder.joinpath(str(number)).open('w'):
                pass

        sub_folder = folder.joinpath("sub")
        sub_folder.mkdir(parents=True, exist_ok=True)
        for number in range(1, 4):
            with sub_folder.joinpath(str(number)).open('w'):
                pass
        folder.joinpath("sub2").mkdir()
        unlink_dir_rec(folder)

        self.assertFalse(folder.exists())

        no_folder = Path("./donotexist/")
        self.assertFalse(no_folder.exists())
        unlink_dir_rec(no_folder)
        self.assertFalse(no_folder.exists())
