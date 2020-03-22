from datetime import datetime

import pytest
from packaging.version import Version, InvalidVersion
from unidown.plugin.link_item_dict import LinkItemDict

from unidown.plugin import PluginInfo
from unidown.plugin.savestate import SaveState


def test_from_json():
    with pytest.raises(ValueError, match=r"version of SaveState does not exist or is empty."):
        SaveState.from_json({'version': '', 'linkItems': {}})
    with pytest.raises(ValueError, match=r"version of SaveState does not exist or is empty."):
        SaveState.from_json({'linkItems': {}})
    with pytest.raises(ValueError, match=r"linkItems of SaveState does not exist."):
        SaveState.from_json({'version': ''})
    with pytest.raises(InvalidVersion, match=r"Savestate version.*"):
        SaveState.from_json({'version': 'dfgdg', 'linkItems': {}})


def test_eq():
    save = SaveState(Version('1'), PluginInfo('name', '1.0.0', 'host'), datetime(1970, 1, 1), LinkItemDict())
    assert not (save == "asdf")
    assert (save != "asdf")


def test_str():
    assert str(PluginInfo('name', '1.0.0', 'host')) == "name - 1.0.0 : host"

