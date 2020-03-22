from datetime import datetime

import pytest

from unidown.plugin import PluginInfo
from unidown.plugin.link_item import LinkItem


def test_from_json():
    with pytest.raises(ValueError, match=r"time is missing"):
        LinkItem.from_json({'name': ''})
    with pytest.raises(ValueError, match=r"name is missing"):
        LinkItem.from_json({'time': ''})


def test_eq():
    item = LinkItem('name', datetime(1970, 1, 1))
    assert not (item == "asdf")
    assert (item != "asdf")


def test_name():
    item = LinkItem('name', datetime(1970, 1, 1))
    with pytest.raises(ValueError, match=r"name cannot be empty or None."):
        item.name = None
    with pytest.raises(ValueError, match=r"name cannot be empty or None."):
        item.name = ''


def test_time():
    item = LinkItem('name', datetime(1970, 1, 1))
    with pytest.raises(ValueError, match=r"time cannot be None."):
        item.time = None
