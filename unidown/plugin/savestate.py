from __future__ import annotations

from datetime import datetime
from typing import Self

from packaging.version import InvalidVersion, Version

from unidown.plugin.link_item import LinkItem
from unidown.plugin.link_item_dict import LinkItemDict
from unidown.plugin.plugin_info import PluginInfo


class SaveState:
    """
    Savestate of a plugin.

    :param version: Savestate version.
    :param plugin_info: Plugin info.
    :param last_update: Last udpate time of the referenced data.
    :param link_items: Data.
    :param version: Savestate version.
    """

    #: Time format to use.
    TIME_FORMAT: str = "%Y%m%dT%H%M%S.%fZ"
    #: Default savestate version.
    _DEFAULT_VERSION: Version = Version('1')

    def __init__(self, plugin_info: PluginInfo, last_update: datetime, link_items: LinkItemDict, version: Version = _DEFAULT_VERSION):
        #: Savestate version.
        self.version: Version = version
        #: Plugin info.
        self.plugin_info: PluginInfo = plugin_info
        #: Newest update time.
        self.last_update: datetime = last_update
        #: Data.
        self.link_items: LinkItemDict = link_items

    def __eq__(self, other: object) -> bool:  # noqa: D105
        if not isinstance(other, self.__class__):
            return False
        return (self.plugin_info == other.plugin_info and self.link_items == other.link_items and self.version == other.version
                and self.last_update == other.last_update
                )

    def __ne__(self, other: object) -> bool:  # noqa: D105
        return not self.__eq__(other)

    def __hash__(self) -> int:  # noqa: D105
        return hash((self.last_update, self.link_items, self.plugin_info, self.version))

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """
        :param data: Json data as dict.
        :return: SaveState.
        :raises ValueError: Version of SaveState does not exist or is empty.
        :raises ~packaging.version.InvalidVersion: Version is not PEP440 conform.
        """
        data_dict = LinkItemDict()
        if 'linkItems' not in data:
            raise ValueError("linkItems of SaveState does not exist.")
        for key, link_item in data['linkItems'].items():
            data_dict[key] = LinkItem.from_json(link_item)
        if 'meta' not in data or 'version' not in data['meta'] or not data['meta']['version']:
            raise ValueError("version of SaveState does not exist or is empty.")
        try:
            version = Version(data['meta']['version'])
        except InvalidVersion as ex:
            raise InvalidVersion(f"Savestate version is not PEP440 conform: {data['meta']['version']}") from ex
        return cls(PluginInfo.from_json(data['pluginInfo']), datetime.strptime(data['lastUpdate'], SaveState.TIME_FORMAT), data_dict, version)

    def to_json(self) -> dict:
        """
        Create json data.

        :return: Json dictionary.
        """
        result: dict = {
            'meta': {'version': str(self.version)},
            'pluginInfo': self.plugin_info.to_json(),
            'lastUpdate': self.last_update.strftime(SaveState.TIME_FORMAT),
            'linkItems': {},
        }
        for key, link_item in self.link_items.items():
            result['linkItems'][key] = link_item.to_json()
        return result

    def upgrade(self) -> Self:
        """
        Upgrading current savestate to the latest savestate version.

        :return: Upgraded savestate.
        """
        return self
