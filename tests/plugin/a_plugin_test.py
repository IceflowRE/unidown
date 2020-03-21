import logging
from datetime import datetime
from pathlib import Path

import pytest
from packaging.version import Version
from unidown_test.plugin import Plugin as TestPlugin

from unidown import dynamic_data
from unidown.plugin import APlugin, LinkItem, PluginException, PluginInfo, SaveState
from unidown.plugin.link_item_dict import LinkItemDict


def create_test_file(file: Path):
    with file.open('wb') as writer:
        writer.write(str.encode('test'))


eg_data = LinkItemDict({
    '/IceflowRE/unidown/master/README.rst':
        LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
    '/IceflowRE/unidown/master/missing':
        LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))
})


def test_equality():
    plugin = TestPlugin()
    assert False == (plugin == "blub")
    assert True == (plugin != "blub")
    plugin_b = TestPlugin()
    assert True == (plugin == plugin_b)
    assert False == (plugin != plugin_b)


def test_init_without_param():
    plugin = TestPlugin()
    assert plugin._log is not None
    assert plugin._simul_downloads == dynamic_data.USING_CORES
    assert plugin.temp_path.exists() and plugin.temp_path.is_dir()
    assert plugin.download_path.exists() and plugin.download_path.is_dir()
    assert isinstance(plugin.log, logging.Logger)
    assert plugin.simul_downloads == dynamic_data.USING_CORES
    assert isinstance(plugin.info, PluginInfo)
    assert plugin.host == 'raw.githubusercontent.com'
    assert plugin.name == 'test'
    assert plugin.version == Version('0.1.0')
    assert plugin.download_path == dynamic_data.DOWNLOAD_DIR.joinpath(plugin.name)
    assert plugin.last_update == datetime(1970, 1, 1)
    assert plugin.download_data == {}
    assert plugin.unit == "item"
    assert plugin.options == {'behaviour': 'normal', 'delay': 0}


def test_init_with_param():
    plugin = TestPlugin(["delay=10.0"])
    assert plugin._options['delay'] == 10.0


def test_init_without_info():
    class Plugin(APlugin):
        def _create_download_links(self) -> LinkItemDict:
            return LinkItemDict()

        def _create_last_update_time(self) -> datetime:
            return datetime(1999, 9, 9, hour=9, minute=9, second=9)

    with pytest.raises(ValueError):
        Plugin()


def test_update_download_links():
    plugin = TestPlugin()
    plugin.update_download_links()
    assert all([a == b for a, b in zip(plugin.download_data, eg_data)])


def test_update_last_update():
    plugin = TestPlugin()
    plugin.update_last_update()
    result = datetime(1999, 9, 9, hour=9, minute=9, second=9)
    assert plugin.last_update == result
    assert result == plugin.last_update


def test_check_download_empty():
    plugin = TestPlugin()
    data = plugin.check_download(LinkItemDict(), plugin._temp_path)
    assert data == (LinkItemDict(), LinkItemDict())


def test_check_download():
    plugin = TestPlugin()

    create_test_file(plugin._temp_path.joinpath('One'))
    data = plugin.check_download(eg_data, plugin._temp_path)
    succeed = LinkItemDict(
        {'/IceflowRE/unidown/master/README.rst': LinkItem('One', datetime(2001, 1, 1, hour=1, minute=1, second=1))}
    )
    lost = LinkItemDict(
        {'/IceflowRE/unidown/master/missing': LinkItem('Two', datetime(2002, 2, 2, hour=2, minute=2, second=2))}
    )
    assert (succeed, lost) == data


def test_clean_up():
    plugin = TestPlugin()
    create_test_file(plugin._temp_path.joinpath('testfile'))
    plugin.clean_up()

    assert plugin._downloader.pool is None
    assert not plugin._temp_path.exists()


def test_delete_data():
    plugin = TestPlugin()
    create_test_file(plugin._temp_path.joinpath('testfile'))
    create_test_file(plugin.download_path.joinpath('testfile'))
    create_test_file(plugin._savestate_file)

    plugin.delete_data()
    assert not plugin._temp_path.exists()
    assert not plugin.download_path.exists()
    assert not plugin._savestate_file.exists()


def test_download_as_file():
    plugin = TestPlugin()
    plugin.download_as_file('/IceflowRE/unidown/master/README.rst', plugin._temp_path, 'file')
    plugin.download_as_file('/IceflowRE/unidown/master/README.rst', plugin._temp_path, 'file')
    plugin.download_as_file('/IceflowRE/unidown/master/README.rst', plugin._temp_path, 'file')
    assert plugin._temp_path.joinpath('file').exists()
    assert plugin._temp_path.joinpath('file_d').exists()
    assert plugin._temp_path.joinpath('file_d_d').exists()


def test_download():
    plugin = TestPlugin()
    plugin.download(eg_data, plugin._temp_path, 'Down units', 'unit')


class TestSaveState:
    def test_update_savestate(self):
        plugin = TestPlugin()
        result = SaveState(dynamic_data.SAVESTATE_VERSION, plugin.info, plugin.last_update, eg_data)
        plugin.update_savestate(eg_data)
        assert result == plugin._savestate

    def test_save_savestate(self):
        plugin = TestPlugin()
        plugin.update_savestate(eg_data)
        plugin.save_savestate()
        with plugin._savestate_file.open(mode='r', encoding="utf8") as data_file:
            json_data = data_file.read()
        assert json_data == '{"version": "1", "pluginInfo": {"name": "test", "version": "0.1.0", "host": "raw.githubusercontent.com"}, "lastUpdate": "19700101T000000.000000Z", "linkItems": {"/IceflowRE/unidown/master/README.rst": {"name": "One", "time": "20010101T010101.000000Z"}, "/IceflowRE/unidown/master/missing": {"name": "Two", "time": "20020202T020202.000000Z"}}}'

    @pytest.mark.parametrize('data', [LinkItemDict(), eg_data])
    def test_normal(self, data):
        plugin = TestPlugin()
        plugin.update_savestate(data)
        plugin.save_savestate()
        plugin.load_savestate()
        assert plugin._savestate == SaveState(dynamic_data.SAVESTATE_VERSION, plugin.info, datetime(1970, 1, 1), data)

    def test_diff_savestate_version(self):
        plugin = TestPlugin()
        plugin.save_savestate()
        dynamic_data.SAVESTATE_VERSION = Version('0.4.2')
        with pytest.raises(PluginException):
            plugin.load_savestate()

    def test_diff_plugin_version(self):
        plugin = TestPlugin()
        plugin.save_savestate()
        plugin._info.version = Version("0.0.1")
        with pytest.raises(PluginException):
            plugin.load_savestate()

    def test_diff_plugin_name(self):
        plugin = TestPlugin()
        plugin.save_savestate()
        plugin._info.name = "different"
        with pytest.raises(PluginException):
            plugin.load_savestate()

    def test_json_error(self):
        plugin = TestPlugin()
        create_test_file(plugin._savestate_file)
        with pytest.raises(PluginException):
            plugin.load_savestate()

    def test_json_error_2(self):
        plugin = TestPlugin()
        with plugin._savestate_file.open('wb') as writer:
            writer.write(str.encode('{}'))
        with pytest.raises(PluginException):
            plugin.load_savestate()


def test_get_plugins():
    assert 'test' in APlugin.get_plugins()
