"""
Test for plugins.a_plugin.
"""

import re
import unittest
from datetime import datetime
from pathlib import Path

from packaging.version import Version

import unidown.core.data.dynamic as dynamic_data
from tests.plugins.test_a_plugin import Plugin
from unidown.core import manager
from unidown.plugins.data.link_item import LinkItem
from unidown.plugins.data.plugin_info import PluginInfo
from unidown.plugins.data.save_state import SaveState
from unidown.plugins.exceptions import PluginException
from unidown.tools.tqdm_option import TqdmOption


class APluginTest(unittest.TestCase):
    """
    Tests for tools.Upgrade.
    """

    def setUp(self):
        manager.init(Path('./tmp'), Path('UniDown.log'), 'INFO')
        dynamic_data.DISABLE_TQDM = True
        self.plugin = Plugin()
        self.plugin.log.disabled = True
        self.eg_data = {'/IceflowRE/Universal-Downloader/master/README.md':
                            LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
                        '/IceflowRE/Universal-Downloader/master/no_file_here':
                            LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}

    def tearDown(self):
        self.plugin.delete_data()

    def test_init(self):
        self.assertTrue(self.plugin.temp_path.exists() and self.plugin.temp_path.is_dir())
        self.assertTrue(self.plugin._download_path.exists() and self.plugin._download_path.is_dir())

    def test_equality(self):
        with self.subTest(desc="different type"):
            self.assertFalse(self.plugin == "blub")
        with self.subTest(desc="equal"):
            plugin = Plugin(PluginInfo('test', '1.0.0', 'raw.githubusercontent.com'))
            self.assertTrue(self.plugin == plugin)
        with self.subTest(desc="unequal"):
            plugin = Plugin(PluginInfo('blub', '1.0.0', 'raw.githubusercontent.com'))
            self.assertFalse(self.plugin == plugin)
            plugin = Plugin(PluginInfo('test', '2.0.0', 'raw.githubusercontent.com'))
            self.assertFalse(self.plugin == plugin)
            plugin = Plugin(PluginInfo('test', '1.0.0', 'www.example.com'))
            self.assertFalse(self.plugin == plugin)

    def test_inequality(self):
        with self.subTest(desc="equal"):
            plugin = Plugin(PluginInfo('test', '1.0.0', 'raw.githubusercontent.com'))
            self.assertFalse(self.plugin != plugin)
        with self.subTest(desc="unequal"):
            plugin = Plugin(PluginInfo('blub', '1.0.0', 'raw.githubusercontent.com'))
            self.assertTrue(self.plugin != plugin)
            plugin = Plugin(PluginInfo('test', '2.0.0', 'raw.githubusercontent.com'))
            self.assertTrue(self.plugin != plugin)
            plugin = Plugin(PluginInfo('test', '1.0.0', 'www.example.com'))
            self.assertTrue(self.plugin != plugin)

    def test_host(self):
        self.assertEqual(self.plugin.host, 'raw.githubusercontent.com')

    def test_name(self):
        self.assertEqual(self.plugin.name, 'test')

    def test_version(self):
        self.assertEqual(self.plugin.version, Version('1.0.0'))

    def test_get_download_links(self):
        result = {'/IceflowRE/Universal-Downloader/master/README.md':
                      LinkItem('README.md', datetime(2000, 1, 1, hour=1, minute=1, second=1)),
                  '/IceflowRE/Universal-Downloader/master/no_file_here':
                      LinkItem('LICENSE', datetime(2002, 2, 2, hour=2, minute=2, second=2))
                  }
        self.assertEqual(result, self.plugin.get_download_links())

    def test_update_last_update(self):
        result = datetime(1999, 9, 9, hour=9, minute=9, second=9)
        time = self.plugin.update_last_update()
        self.assertEqual(time, result)
        self.assertEqual(result, self.plugin.last_update)

    def test_check_download(self):
        with self.subTest(desc="empty"):
            data = self.plugin.check_download({}, self.plugin.temp_path)
            self.assertEqual(({}, {}), data)

        with self.subTest(desc="one succeed, one lost"):
            create_test_file(self.plugin.temp_path.joinpath('One'))
            data = self.plugin.check_download(self.eg_data, self.plugin.temp_path)
            succeed = {'/IceflowRE/Universal-Downloader/master/README.md':
                           LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}
            lost = {'/IceflowRE/Universal-Downloader/master/no_file_here':
                        LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}
            self.assertEqual((succeed, lost), data)

    def test_clean_up(self):
        create_test_file(self.plugin.temp_path.joinpath('testfile'))
        self.plugin.clean_up()

        self.assertFalse(self.plugin.temp_path.exists())

    def test_delete_data(self):
        create_test_file(self.plugin.temp_path.joinpath('testfile'))
        create_test_file(self.plugin._download_path.joinpath('testfile'))
        create_test_file(self.plugin.save_state_file)

        self.plugin.delete_data()
        self.assertFalse(self.plugin.temp_path.exists())
        self.assertFalse(self.plugin._download_path.exists())
        self.assertFalse(self.plugin.save_state_file.exists())

    def test_download_as_file(self):
        self.plugin.download_as_file('/IceflowRE/Universal-Downloader/master/README.md',
                                     self.plugin.temp_path, 'file')
        self.assertTrue(self.plugin.temp_path.joinpath('file').exists())
        self.plugin.download_as_file('/IceflowRE/Universal-Downloader/master/README.md',
                                     self.plugin.temp_path, 'file')
        self.assertTrue(self.plugin.temp_path.joinpath('file_d').exists())
        self.plugin.download_as_file('/IceflowRE/Universal-Downloader/master/README.md',
                                     self.plugin.temp_path, 'file')
        self.assertTrue(self.plugin.temp_path.joinpath('file_d_d').exists())

    def test_download(self):
        with self.subTest(desc="no item"):
            self.plugin.download({}, self.plugin.temp_path, TqdmOption('Down units', 'unit'))

        with self.subTest(desc="one success, one fail"):
            data = self.plugin.download(self.eg_data, self.plugin.temp_path, TqdmOption('Down units', 'unit'))
            self.assertEqual(['/IceflowRE/Universal-Downloader/master/README.md'], data)

    def test_create_save_state(self):
        result = SaveState(dynamic_data.SAVE_STATE_VERSION, self.plugin.last_update, self.plugin.info,
                           self.eg_data)
        self.assertEqual(result, self.plugin._create_save_state(self.eg_data))

    def test_save_save_state(self):
        self.plugin.save_save_state(self.eg_data)
        with self.plugin.save_state_file.open(mode='r', encoding="utf8") as data_file:
            json_data = data_file.read()
        regexp = re.compile(r'"data":\s{([\s\S]+"\s+}\s)')
        try:
            data = regexp.search(json_data).group(1)
        except AttributeError:
            self.fail("No data part found.")
        items = [
""""/IceflowRE/Universal-Downloader/master/README.md": {
      "name": "One",
      "time": "2001-01-01T01:01:01Z"
    }""",
""""/IceflowRE/Universal-Downloader/master/no_file_here": {
      "name": "Two",
      "time": "2002-02-02T02:02:02Z"
    }"""]
        print(data)
        for item in items:
            with self.subTest():
                if data.find(item) == -1:
                    self.fail("{item} | not found.".format(item=item))

    def test_load_save_savestate(self):
        with self.subTest(desc="default return"):
            result = SaveState(dynamic_data.SAVE_STATE_VERSION, datetime(1970, 1, 1),
                               PluginInfo('test', '1.0.0', 'raw.githubusercontent.com'), {})
            self.assertEqual(result, self.plugin.load_save_state())

        with self.subTest(desc="load without errors"):
            self.plugin.save_save_state(self.eg_data)
            save_state = self.plugin.load_save_state()
            result = SaveState(dynamic_data.SAVE_STATE_VERSION, self.plugin.last_update, self.plugin.info,
                               self.eg_data)
            self.assertEqual(save_state, result)

        with self.subTest(desc="different save state version"):
            plugin = Plugin(PluginInfo("test", "1.0.0", "host"))
            plugin.save_save_state(self.eg_data)
            dynamic_data.SAVE_STATE_VERSION = Version('0.4.2')
            with self.assertRaises(PluginException):
                plugin.load_save_state()
            self.setUp()

        with self.subTest(desc="different plugin version"):
            plugin = Plugin(PluginInfo("test", "1.0.0", "host"))
            plugin.save_save_state(self.eg_data)
            plugin = Plugin(PluginInfo("test", "2.0.0", "host"))
            with self.assertRaises(PluginException):
                plugin.load_save_state()

        with self.subTest(desc="different plugin name"):
            plugin = Plugin(PluginInfo("test", "1.0.0", "host"))
            plugin.save_save_state(self.eg_data)
            plugin._info.name = "different"
            with self.assertRaises(PluginException):
                plugin.load_save_state()

    def test_compare_old_with_new_data(self):
        with self.subTest(desc='empty with empty'):
            self.assertEqual({}, self.plugin.compare_old_with_new_data({}, {}))

        with self.subTest(desc='filled with filled and the same'):
            self.assertEqual({}, self.plugin.compare_old_with_new_data(self.eg_data, self.eg_data))

        with self.subTest(desc='empty with filled'):
            self.assertEqual(self.eg_data, self.plugin.compare_old_with_new_data({}, self.eg_data))

        with self.subTest(desc='filled with empty'):
            self.assertEqual({}, self.plugin.compare_old_with_new_data(self.eg_data, {}))

        with self.subTest(desc='filled with one item more'):
            old_data = {'/IceflowRE/Universal-Downloader/master/README.md':
                            LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}
            result = {'/IceflowRE/Universal-Downloader/master/no_file_here':
                          LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}
            self.assertEqual(result, self.plugin.compare_old_with_new_data(old_data, self.eg_data))

        with self.subTest(desc='one item more with filled'):
            new_data = {'/IceflowRE/Universal-Downloader/master/no_file_here':
                            LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}
            self.assertEqual({}, self.plugin.compare_old_with_new_data(self.eg_data, new_data))


def create_test_file(file: Path):
    with open(file, 'wb') as writer:
        writer.write(str.encode('test'))
