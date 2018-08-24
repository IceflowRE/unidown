import unittest
from pathlib import Path

from unidown import dynamic_data
from unidown.core import manager
from unidown.core.plugin_state import PluginState


class ManagerTest(unittest.TestCase):
    def test_init(self):
        for path in [Path('./tmp'), Path('./tmp2/tmp')]:
            manager.init(path, Path('UniDown.log'), dynamic_data.LOG_LEVEL)
            with self.subTest(path=str(path), logfile='UniDown.log', loglevel=dynamic_data.LOG_LEVEL):
                self.assertTrue(path.joinpath('downloads').exists())
                self.assertTrue(path.joinpath('savestates').exists())
                self.assertTrue(path.joinpath('temp').exists())
                self.assertTrue(path.joinpath('UniDown.log').is_file())

    def test_run(self):
        with self.subTest(desc="not existing plugin"):
            self.assertEqual(manager.run("not_existing_plugin"), PluginState.NOT_FOUND)

        with self.subTest(desc="crash while loading"):
            self.assertEqual(manager.run("test", ["behaviour=load_crash"]), PluginState.LOAD_CRASH)

        with self.subTest(desc="stopped working"):
            self.assertEqual(manager.run("test", ["behaviour=run_fail"]), PluginState.RUN_FAIL)

        with self.subTest(desc="not existing plugin"):
            self.assertEqual(manager.run("test", ["behaviour=run_crash"]), PluginState.RUN_CRASH)

        with self.subTest(desc="success"):
            self.assertEqual(manager.run("test", ["behaviour=normal"]), PluginState.END_SUCCESS)
