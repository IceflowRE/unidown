from __future__ import annotations

from datetime import datetime
from typing import Dict

from google.protobuf.timestamp_pb2 import Timestamp
from packaging.version import InvalidVersion, Version

from unidown.plugin.link_item import LinkItem
from unidown.plugin.plugin_info import PluginInfo
from unidown.plugin.protobuf.save_state_pb2 import SaveStateProto
from unidown.tools import datetime_to_timestamp


class SaveState:
    """
    Savestate of a plugin.

    :param version: savestate version
    :type version: ~packaging.version.Version
    :param plugin_info: plugin info
    :type plugin_info: ~unidown.plugin.plugin_info.PluginInfo
    :param last_update: last udpate time of the referenced data
    :type last_update: ~datetime.datetime
    :param link_item_dict: data
    :type link_item_dict: dict[str, ~unidown.plugin.link_item.LinkItem]

    :ivar version: savestate version
    :vartype version: ~packaging.version.Version
    :ivar plugin_info: plugin info
    :vartype plugin_info: ~unidown.plugin.plugin_info.PluginInfo
    :ivar last_update: newest udpate time
    :vartype last_update: ~datetime.datetime
    :ivar link_item_dict: data
    :vartype link_item_dict: Dict[str, ~unidown.plugin.link_item.LinkItem]
    """

    def __init__(self, version: Version, plugin_info: PluginInfo, last_update: datetime,
                 link_item_dict: Dict[str, LinkItem]):
        self.version = version
        self.plugin_info = plugin_info
        self.last_update = last_update
        self.link_item_dict = link_item_dict

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.plugin_info == other.plugin_info and self.link_item_dict == other.link_item_dict and \
               self.version == other.version and self.last_update == other.last_update

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @classmethod
    def from_protobuf(cls, proto: SaveStateProto) -> SaveState:
        """
        Constructor from protobuf. Can raise ValueErrors from called from_protobuf() parsers.

        :param proto: protobuf structure
        :type proto: ~unidown.plugin.protobuf.save_state_pb2.SaveStateProto
        :return: the SaveState
        :rtype: ~unidown.plugin.save_state.SaveState
        :raises ValueError: version of SaveState does not exist or is empty inside the protobuf
        :raises ~packaging.version.InvalidVersion: version is not PEP440 conform
        """
        data_dict = {}
        for key, link_item in proto.data.items():
            data_dict[key] = LinkItem.from_protobuf(link_item)
        if proto.version == "":
            raise ValueError("version of SaveState does not exist or is empty inside the protobuf.")
        try:
            version = Version(proto.version)
        except InvalidVersion:
            raise InvalidVersion(f"Plugin version is not PEP440 conform: {proto.version}")
        return cls(version, PluginInfo.from_protobuf(proto.plugin_info), Timestamp.ToDatetime(proto.last_update),
                   data_dict)

    def to_protobuf(self) -> SaveStateProto:
        """
        Create protobuf item.

        :return: protobuf structure
        :rtype: ~unidown.plugin.protobuf.save_state_pb2.SaveStateProto
        """
        result = SaveStateProto()
        result.version = str(self.version)
        result.last_update.CopyFrom(datetime_to_timestamp(self.last_update))
        result.plugin_info.CopyFrom(self.plugin_info.to_protobuf())
        for key, link_item in self.link_item_dict.items():
            result.data[key].CopyFrom(link_item.to_protobuf())
        return result
