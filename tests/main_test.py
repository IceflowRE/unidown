import unittest
from pathlib import Path

from unidown import dynamic_data
from unidown.main import main


class MainTest(unittest.TestCase):
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
        with self.subTest(desc="no delay"):
            with self.assertRaises(SystemExit) as se:
                main(['--main', './test-tmp/test_main/', '--plugin', 'test', '--log', 'CRITICAL'])

            self.assertEqual(se.exception.code, 0)
            self.assertTrue(Path('./test-tmp/test_main/savestates/test_save.json').exists())
            self.assertTrue(Path('./test-tmp/test_main/downloads/test/README.rst').exists())
        with self.subTest(desc="print list"):
            with self.assertRaises(SystemExit) as se:
                main(['--list-plugins'])

            self.assertEqual(se.exception.code, 0)
