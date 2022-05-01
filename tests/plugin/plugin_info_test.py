import pytest
from packaging.version import InvalidVersion

from unidown.plugin import PluginInfo


def test_init():
    with pytest.raises(ValueError, match=r"Plugin parameter 'name' cannot be empty."):
        PluginInfo("", '1.0.0', 'host')
    with pytest.raises(ValueError, match=r"Plugin parameter 'host' cannot be empty."):
        PluginInfo("name", '1.0.0', '')
    with pytest.raises(InvalidVersion):
        PluginInfo("name", '', 'host')
    with pytest.raises(InvalidVersion):
        PluginInfo("name", '1dfg15', 'host')


def test_from_json():
    with pytest.raises(ValueError, match=r"name is missing"):
        PluginInfo.from_json({'version': '1.0.0', 'host': 'host'})
    with pytest.raises(ValueError, match=r"version is missing"):
        PluginInfo.from_json({'name': 'name', 'host': 'host'})
    with pytest.raises(ValueError, match=r"host is missing"):
        PluginInfo.from_json({'name': 'name', 'version': '1.0.0'})


def test_eq():
    assert not (PluginInfo('name', '1.0.0', 'host') == "blub")
    assert (PluginInfo('name', '1.0.0', 'host') != "blub")


def test_str():
    assert str(PluginInfo('name', '1.0.0', 'host')) == "name - 1.0.0 : host"
