import unittest
from pathlib import Path

from unidown import dynamic_data


class DynamicDataTest(unittest.TestCase):
    def tearDown(self):
        dynamic_data.reset()

    def test_check_dir(self):
        path = Path("./test-tmp/test_check_dir/")
        path.mkdir(parents=True, exist_ok=False)
        file = path.joinpath("temp.text")
        with file.open('w'):
            pass

        dynamic_data.MAIN_DIR = file
        with self.assertRaises(FileExistsError):
            dynamic_data.check_dirs()
