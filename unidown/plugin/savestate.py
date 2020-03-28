from __future__ import annotations

from datetime import datetime

from packaging.version import InvalidVersion, Version

from unidown.plugin.link_item import LinkItem
from unidown.plugin.link_item_dict import LinkItemDict
from unidown.plugin.plugin_info import PluginInfo


class SaveState:
    """
    Savestate of a plugin.

    :param version: savestate version
    :param plugin_info: plugin info
    :param last_update: last udpate time of the referenced data
    :param link_items: data
    :param version: savestate version

    :cvar time_format: time format to use
    :ivar version: savestate version
    :ivar plugin_info: plugin info
    :ivar last_update: newest udpate time
    :ivar link_items: data
    """
    # current savestate version which will be used
    time_format: str = "%Y%m%dT%H%M%S.%fZ"

    def __init__(self, plugin_info: PluginInfo, last_update: datetime, link_items: LinkItemDict,
                 version: Version = Version('1')):
        self.version: Version = version
        self.plugin_info: PluginInfo = plugin_info
        self.last_update: datetime = last_update
        self.link_items: LinkItemDict = link_items

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self.plugin_info == other.plugin_info and self.link_items == other.link_items and self.version == other.version and
                self.last_update == other.last_update)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @classmethod
    def from_json(cls, data: dict) -> SaveState:
        """
        :param data: json data as dict
        :return: the SaveState
        :raises ValueError: version of SaveState does not exist or is empty
        :raises ~packaging.version.InvalidVersion: version is not PEP440 conform
        """
        data_dict = LinkItemDict()
        if 'linkItems' not in data:
            raise ValueError("linkItems of SaveState does not exist.")
        for key, link_item in data['linkItems'].items():
            data_dict[key] = LinkItem.from_json(link_item)
        if 'meta' not in data or 'version' not in data['meta'] or data['meta']['version'] == "":
            raise ValueError("version of SaveState does not exist or is empty.")
        try:
            version = Version(data['meta']['version'])
        except InvalidVersion:
            raise InvalidVersion(f"Savestate version is not PEP440 conform: {data['meta']['version']}")
        return cls(PluginInfo.from_json(data['pluginInfo']), datetime.strptime(data['lastUpdate'], SaveState.time_format), data_dict, version)

    def to_json(self) -> dict:
        """
        Create json data.

        :return: json dictionary
        """
        result = {
            'meta': {'version': str(self.version)},
            'pluginInfo': self.plugin_info.to_json(),
            'lastUpdate': self.last_update.strftime(SaveState.time_format),
            'linkItems': {},
        }
        for key, link_item in self.link_items.items():
            result['linkItems'][key] = link_item.to_json()
        return result

    def upgrade(self) -> SaveState:
        """
        Upgrading current savestate to the latest savestate version.

        :return: upgraded savestate
        """
        return self
