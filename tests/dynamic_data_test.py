import unittest
from pathlib import Path

from unidown import dynamic_data


class DynamicDataTest(unittest.TestCase):
    def tearDown(self):
        dynamic_data.reset()

    def test_check_dir(self):
        path = Path("./tmp/temp.txt")
        with path.open('w'):
            pass

        dynamic_data.MAIN_DIR = path
        with self.assertRaises(FileExistsError):
            dynamic_data.check_dirs()
