"""
Test for plugins.a_plugin.
"""
import logging
import re
import unittest
from datetime import datetime
from pathlib import Path

import pkg_resources
from packaging.version import Version

from unidown import dynamic_data
from unidown.core import manager
from unidown.plugin.a_plugin import APlugin
from unidown.plugin.exceptions import PluginException
from unidown.plugin.link_item import LinkItem
from unidown.plugin.plugin_info import PluginInfo
from unidown.plugin.save_state import SaveState


class APluginLayer(object):
    @classmethod
    def setUp(cls):
        cls.test_plugin = None
        for entry in pkg_resources.iter_entry_points('unidown.plugin'):
            if entry.name == "test":
                cls.test_plugin = entry.load()


class APluginTest(unittest.TestCase):
    layer = APluginLayer

    def setUp(self):
        manager.init(Path('./tmp'), Path('UniDown.log'), 'INFO')
        dynamic_data.DISABLE_TQDM = True
        if self.layer.test_plugin is None:
            self.fail("Test plugin could not be loaded or was not found.")
        self.plugin = self.layer.test_plugin()
        self.plugin.log.disabled = True
        self.eg_data = {'/IceflowRE/Universal-Downloader/master/README.rst':
                            LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
                        '/IceflowRE/Universal-Downloader/master/no_file_here':
                            LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}

    def tearDown(self):
        self.plugin.delete_data()

    def test_init(self):
        with self.subTest(desc="without parameter"):
            self.assertTrue(self.plugin._temp_path.exists() and self.plugin._temp_path.is_dir())
            self.assertTrue(self.plugin.download_path.exists() and self.plugin.download_path.is_dir())

            self.assertIsInstance(self.plugin.log, logging.Logger)
            self.assertEqual(self.plugin.simul_downloads, dynamic_data.USING_CORES)
            self.assertIsInstance(self.plugin.info, PluginInfo)
            self.assertEqual(self.plugin.host, 'raw.githubusercontent.com')
            self.assertEqual(self.plugin.name, 'test')
            self.assertEqual(self.plugin.version, Version('1.0.0'))
            self.assertEqual(self.plugin.download_path, dynamic_data.DOWNLOAD_DIR.joinpath(self.plugin.name))
            self.assertEqual(self.plugin.last_update, datetime(1970, 1, 1))
            self.assertEqual(self.plugin.download_data, {})
            self.assertEqual(self.plugin.unit, "item")
        with self.subTest(desc="with parameter"):
            plugin = self.layer.test_plugin(["delay=10.0"])
            self.assertEqual(plugin._options['delay'], 10.0)

    def test_equality(self):
        with self.subTest(desc="different type"):
            self.assertFalse(self.plugin == "blub")
            self.assertTrue(self.plugin != "blub")
        with self.subTest(desc="equal"):
            plugin = self.layer.test_plugin(None, PluginInfo('test', '1.0.0', 'raw.githubusercontent.com'))
            self.assertTrue(self.plugin == plugin)
            self.assertFalse(self.plugin != plugin)
        with self.subTest(desc="unequal"):
            plugin = self.layer.test_plugin(None, PluginInfo('blub', '1.0.0', 'raw.githubusercontent.com'))
            self.assertFalse(self.plugin == plugin)
            self.assertTrue(self.plugin != plugin)
            plugin = self.layer.test_plugin(None, PluginInfo('test', '2.0.0', 'raw.githubusercontent.com'))
            self.assertFalse(self.plugin == plugin)
            self.assertTrue(self.plugin != plugin)
            plugin = self.layer.test_plugin(None, PluginInfo('test', '1.0.0', 'www.example.com'))
            self.assertFalse(self.plugin == plugin)
            self.assertTrue(self.plugin != plugin)

    def test_update_download_links(self):
        result = {'/IceflowRE/Universal-Downloader/master/README.rst':
                      LinkItem('README.rst', datetime(2000, 1, 1, hour=1, minute=1, second=1)),
                  '/IceflowRE/Universal-Downloader/master/no_file_here':
                      LinkItem('LICENSE', datetime(2002, 2, 2, hour=2, minute=2, second=2))
                  }
        self.plugin.update_download_links()

        self.assertEqual(result, self.plugin.download_data)

    def test_update_last_update(self):
        result = datetime(1999, 9, 9, hour=9, minute=9, second=9)
        self.plugin.update_last_update()
        self.assertEqual(self.plugin.last_update, result)
        self.assertEqual(result, self.plugin.last_update)

    def test_check_download(self):
        with self.subTest(desc="empty"):
            data = self.plugin.check_download({}, self.plugin._temp_path)
            self.assertEqual(({}, {}), data)

        with self.subTest(desc="one succeed, one lost"):
            create_test_file(self.plugin._temp_path.joinpath('One'))
            data = self.plugin.check_download(self.eg_data, self.plugin._temp_path)
            succeed = {'/IceflowRE/Universal-Downloader/master/README.rst':
                           LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}
            lost = {'/IceflowRE/Universal-Downloader/master/no_file_here':
                        LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}
            self.assertEqual((succeed, lost), data)

    def test_clean_up(self):
        create_test_file(self.plugin._temp_path.joinpath('testfile'))
        self.plugin.clean_up()

        self.assertEqual(self.plugin._downloader.pool, None)
        self.assertFalse(self.plugin._temp_path.exists())

    def test_delete_data(self):
        create_test_file(self.plugin._temp_path.joinpath('testfile'))
        create_test_file(self.plugin.download_path.joinpath('testfile'))
        create_test_file(self.plugin._save_state_file)

        self.plugin.delete_data()
        self.assertFalse(self.plugin._temp_path.exists())
        self.assertFalse(self.plugin.download_path.exists())
        self.assertFalse(self.plugin._save_state_file.exists())

    def test_download_as_file(self):
        self.plugin.download_as_file('/IceflowRE/Universal-Downloader/master/README.rst',
                                     self.plugin._temp_path, 'file')
        self.assertTrue(self.plugin._temp_path.joinpath('file').exists())
        self.plugin.download_as_file('/IceflowRE/Universal-Downloader/master/README.rst',
                                     self.plugin._temp_path, 'file')
        self.assertTrue(self.plugin._temp_path.joinpath('file_d').exists())
        self.plugin.download_as_file('/IceflowRE/Universal-Downloader/master/README.rst',
                                     self.plugin._temp_path, 'file')
        self.assertTrue(self.plugin._temp_path.joinpath('file_d_d').exists())

    def test_download(self):
        with self.subTest(desc="no item"):
            self.plugin.download({}, self.plugin._temp_path, 'Down units', 'unit')

        with self.subTest(desc="one success, one fail"):
            data = self.plugin.download(self.eg_data, self.plugin._temp_path, 'Down units', 'unit')
            self.assertEqual(['/IceflowRE/Universal-Downloader/master/README.rst'], data)

    def test_create_save_state(self):
        result = SaveState(dynamic_data.SAVE_STATE_VERSION, self.plugin.info, self.plugin.last_update, self.eg_data)
        self.assertEqual(result, self.plugin._create_save_state(self.eg_data))

    def test_save_save_state(self):
        self.plugin.save_save_state(self.eg_data)
        with self.plugin._save_state_file.open(mode='r', encoding="utf8") as data_file:
            json_data = data_file.read()
        regexp = re.compile(r'"data":\s{([\s\S]+"\s+}\s)')
        try:
            data = regexp.search(json_data).group(1)
        except AttributeError:
            self.fail("No data part found.")
        items = [
            ('"/IceflowRE/Universal-Downloader/master/README.rst": {' '\n'
             '      "name": "One",' '\n'
             '      "time": "2001-01-01T01:01:01Z"' '\n'
             '    }'),
            ('"/IceflowRE/Universal-Downloader/master/no_file_here": {' '\n'
             '      "name": "Two",' '\n'
             '      "time": "2002-02-02T02:02:02Z"' '\n'
             '    }')
        ]
        for item in items:
            with self.subTest():
                if data.find(item) == -1:
                    self.fail(f"{item} | not found.")

    def test_load_save_savestate(self):
        with self.subTest(desc="default return"):
            result = SaveState(dynamic_data.SAVE_STATE_VERSION,
                               PluginInfo('test', '1.0.0', 'raw.githubusercontent.com'), datetime(1970, 1, 1), {})
            self.assertEqual(result, self.plugin.load_save_state())

        with self.subTest(desc="load without errors"):
            self.plugin.save_save_state(self.eg_data)
            save_state = self.plugin.load_save_state()
            result = SaveState(dynamic_data.SAVE_STATE_VERSION, self.plugin.info, self.plugin.last_update, self.eg_data)
            self.assertEqual(save_state, result)

        with self.subTest(desc="different save state version"):
            plugin = self.layer.test_plugin(None, PluginInfo("test", "1.0.0", "host"))
            plugin.save_save_state(self.eg_data)
            dynamic_data.SAVE_STATE_VERSION = Version('0.4.2')
            with self.assertRaises(PluginException):
                plugin.load_save_state()
            self.setUp()

        with self.subTest(desc="different plugin version"):
            plugin = self.layer.test_plugin(None, PluginInfo("test", "1.0.0", "host"))
            plugin.save_save_state(self.eg_data)
            plugin = self.layer.test_plugin(None, PluginInfo("test", "2.0.0", "host"))
            with self.assertRaises(PluginException):
                plugin.load_save_state()

        with self.subTest(desc="different plugin name"):
            plugin = self.layer.test_plugin(None, PluginInfo("test", "1.0.0", "host"))
            plugin.save_save_state(self.eg_data)
            plugin._info.name = "different"
            with self.assertRaises(PluginException):
                plugin.load_save_state()

        with self.subTest(desc="json parse error"):
            create_test_file(self.plugin._save_state_file)
            with self.assertRaises(PluginException):
                self.plugin.load_save_state()

        with self.subTest(desc="json parse error"):
            with open(self.plugin._save_state_file, 'wb') as writer:
                writer.write(str.encode('{}'))
            with self.assertRaises(PluginException):
                self.plugin.load_save_state()

    def test_get_updated_data(self):
        with self.subTest(desc='empty with empty'):
            self.plugin._download_data = {}
            self.assertEqual({}, self.plugin.get_updated_data({}))

        with self.subTest(desc='filled with filled and the same'):
            self.plugin._download_data = self.eg_data
            self.assertEqual({}, self.plugin.get_updated_data(self.eg_data))

        with self.subTest(desc='empty with filled'):
            self.plugin._download_data = self.eg_data
            self.assertEqual(self.eg_data, self.plugin.get_updated_data({}))

        with self.subTest(desc='filled with empty'):
            self.plugin._download_data = {}
            self.assertEqual({}, self.plugin.get_updated_data(self.eg_data))

        with self.subTest(desc='filled with one item more'):
            old_data = {'/IceflowRE/Universal-Downloader/master/README.rst':
                            LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}
            result = {'/IceflowRE/Universal-Downloader/master/no_file_here':
                          LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}
            self.plugin._download_data = self.eg_data
            self.assertEqual(result, self.plugin.get_updated_data(old_data))

        with self.subTest(desc='one item more with filled'):
            new_data = {'/IceflowRE/Universal-Downloader/master/no_file_here':
                            LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}
            self.plugin._download_data = new_data
            self.assertEqual({}, self.plugin.get_updated_data(self.eg_data))

    def test_get_plugins(self):
        """
        This test requires that the unidown test plugin is installed.
        """
        self.assertIn('test', APlugin.get_plugins())


def create_test_file(file: Path):
    with open(file, 'wb') as writer:
        writer.write(str.encode('test'))
