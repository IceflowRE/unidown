import unittest
from pathlib import Path

from unidown import dynamic_data
from unidown.main import main


class DynamicDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dynamic_data.DISABLE_TQDM = True

    def test_main(self):
        """
        This just runs the main for the test plugin. Nothing else is done.

        Missing:
        - argument testing
        - ...
        """
        with self.assertRaises(SystemExit) as se:
            main(['--main', './tmp/', '--plugin', 'test', '--log', 'CRITICAL'])

        self.assertEqual(se.exception.code, 0)
        self.assertTrue(Path('./tmp/savestates/test_save.json').exists())
        self.assertTrue(Path('./tmp/downloads/test/README.rst').exists())
