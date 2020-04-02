import logging
from datetime import datetime
from pathlib import Path

import pytest
from packaging.version import Version
from unidown_test.plugin import Plugin as TestPlugin
from unidown_test.savestate import MySaveState

from unidown.core.manager import get_options
from unidown.core.settings import Settings
from unidown.plugin import APlugin, LinkItem, PluginException, PluginInfo
from unidown.plugin.link_item_dict import LinkItemDict


def create_test_file(file: Path):
    with file.open('wb') as writer:
        writer.write(str.encode('test'))


eg_data = LinkItemDict({
    '/IceflowRE/unidown/master/README.rst': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
    '/IceflowRE/unidown/master/LICENSE.md': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
    '/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))
})


def test_equality(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    assert False == (plugin == "blub")
    assert True == (plugin != "blub")
    plugin_b = TestPlugin(Settings(tmp_path))
    assert True == (plugin == plugin_b)
    assert False == (plugin != plugin_b)


def test_init_without_param(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    settings = Settings(tmp_path)
    assert plugin._log is not None
    assert plugin.temp_dir.exists() and plugin.temp_dir.is_dir()
    assert plugin.download_dir.exists() and plugin.download_dir.is_dir()
    assert isinstance(plugin.log, logging.Logger)
    assert plugin.simul_downloads == settings.cores
    assert isinstance(plugin.info, PluginInfo)
    assert plugin.host == 'raw.githubusercontent.com'
    assert plugin.name == 'test'
    assert plugin.version == Version('0.1.0')
    assert plugin.download_dir == settings.download_dir.joinpath(plugin.name)
    assert plugin.last_update == datetime(1970, 1, 1)
    assert plugin.download_data == {}
    assert plugin.unit == "item"
    assert plugin.options == {'behaviour': 'normal', 'delay': 0, 'username': ''}
    assert plugin._username == ''


def test_init_with_param(tmp_path):
    plugin = TestPlugin(Settings(tmp_path), get_options([["delay=10.0"]]))
    assert plugin._options['delay'] == 10.0


def test_init_without_info(tmp_path):
    class Plugin(APlugin):
        def _create_download_data(self) -> LinkItemDict:
            return LinkItemDict()

        def _create_last_update_time(self) -> datetime:
            return datetime(1999, 9, 9, hour=9, minute=9, second=9)

    with pytest.raises(ValueError):
        Plugin(Settings(tmp_path))


def test_update_download_data(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    plugin.update_download_data()
    assert all([a == b for a, b in zip(plugin.download_data.items(), eg_data.items())])


def test_update_last_update(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    plugin.update_last_update()
    result = datetime(1999, 9, 9, hour=9, minute=9, second=9)
    assert plugin.last_update == result
    assert result == plugin.last_update


def test_check_download_empty(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    data = plugin.check_download(LinkItemDict(), plugin._temp_dir)
    assert data == (LinkItemDict(), LinkItemDict())


def test_check_download(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))

    create_test_file(plugin._temp_dir.joinpath('README.rst'))
    data = plugin.check_download(eg_data, plugin._temp_dir)
    succeed = LinkItemDict({
        '/IceflowRE/unidown/master/README.rst': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
        '/IceflowRE/unidown/master/LICENSE.md': LinkItem('README.rst', datetime(2001, 1, 1, hour=1, minute=1, second=1)),
    })
    lost = LinkItemDict({
        '/IceflowRE/unidown/master/missing': LinkItem('missing', datetime(2002, 2, 2, hour=2, minute=2, second=2))
    })
    assert (succeed, lost) == data


def test_clean_up(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    create_test_file(plugin._temp_dir.joinpath('testfile'))
    plugin.clean_up()

    assert plugin._downloader.pool is None
    assert not plugin._temp_dir.exists()


def test_download_as_file(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    plugin.download_as_file('/IceflowRE/unidown/master/README.rst', plugin._temp_dir.joinpath('file.test'))
    plugin.download_as_file('/IceflowRE/unidown/master/README.rst', plugin._temp_dir.joinpath('file.test'))
    plugin.download_as_file('/IceflowRE/unidown/master/README.rst', plugin._temp_dir.joinpath('file.test'))
    assert plugin._temp_dir.joinpath('file.test').exists()
    assert plugin._temp_dir.joinpath('file_r.test').exists()
    assert plugin._temp_dir.joinpath('file_r_r.test').exists()


def test_download(tmp_path):
    plugin = TestPlugin(Settings(tmp_path))
    plugin.download(eg_data, plugin._temp_dir, 'Down units', 'unit')


class TestSaveState:
    def test_update_savestate(self, tmp_path):
        plugin = TestPlugin(Settings(tmp_path))
        result = MySaveState(plugin.info, plugin.last_update, eg_data)
        plugin.update_savestate(eg_data)
        assert result == plugin._savestate

    def test_save_savestate(self, tmp_path):
        plugin = TestPlugin(Settings(tmp_path))
        plugin.update_savestate(eg_data)
        plugin.save_savestate()
        with plugin._savestate_file.open(encoding="utf8") as reader:
            json_data = reader.read()
        assert json_data == '{"meta": {"version": "1"}, "pluginInfo": {"name": "test", "version": "0.1.0", "host": "raw.githubusercontent.com"}, "lastUpdate": "19700101T000000.000000Z", "linkItems": {"/IceflowRE/unidown/master/README.rst": {"name": "README.rst", "time": "20010101T010101.000000Z"}, "/IceflowRE/unidown/master/LICENSE.md": {"name": "README.rst", "time": "20010101T010101.000000Z"}, "/IceflowRE/unidown/master/missing": {"name": "missing", "time": "20020202T020202.000000Z"}}, "username": ""}'

    @pytest.mark.parametrize('data', [LinkItemDict(), eg_data])
    def test_normal(self, tmp_path, data):
        plugin = TestPlugin(Settings(tmp_path))
        plugin._username = 'Nasua Nasua'
        plugin.update_savestate(data)
        plugin.save_savestate()
        plugin.load_savestate()
        result = MySaveState(plugin.info, datetime(1970, 1, 1), data)
        result.username = "Nasua Nasua"
        assert plugin._savestate == result

    def test_diff_plugin_name(self, tmp_path):
        plugin = TestPlugin(Settings(tmp_path))
        plugin.save_savestate()
        plugin._info.name = "different"
        with pytest.raises(PluginException):
            plugin.load_savestate()

    def test_json_error(self, tmp_path):
        plugin = TestPlugin(Settings(tmp_path))
        create_test_file(plugin._savestate_file)
        with pytest.raises(PluginException):
            plugin.load_savestate()

    def test_json_error_2(self, tmp_path):
        plugin = TestPlugin(Settings(tmp_path))
        with plugin._savestate_file.open('wb') as writer:
            writer.write(str.encode('{}'))
        with pytest.raises(PluginException):
            plugin.load_savestate()


def test_load_default_options(tmp_path, caplog):
    plugin = TestPlugin(Settings(tmp_path), {})
    plugin._load_default_options()
    plugin = TestPlugin(Settings(tmp_path), {'delay': 'float', 'behaviour': 'normal'})
    plugin._load_default_options()
    result = [
        "Plugin option 'delay' is missing. Using 0s.",
        "Plugin option 'behaviour' is missing. Using default.",
        "Plugin option 'delay' was not a float. Using 0s."
    ]
    assert len(caplog.records) == len(result)
    for actual, expect in zip(caplog.records, result):
        assert actual.msg == expect


def test_get_plugins():
    assert 'test' in APlugin.get_plugins()
