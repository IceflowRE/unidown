from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp
from packaging.version import InvalidVersion, Version

from unidown.plugins.data.link_item import LinkItem
from unidown.plugins.data.plugin_info import PluginInfo
from unidown.plugins.data.protobuf.save_state_pb2 import SaveStateProto
from unidown.tools.tools import datetime_to_timestamp


class SaveState:
    """
    Savestate of a plugin.

    :param version: savestate version
    :type version: ~packaging.version.Version
    :param last_update: last udpate time of the referenced data
    :type last_update: ~datetime.datetime
    :param plugin_info: plugin info
    :type plugin_info: ~unidown.plugins.data.plugin_info.PluginInfo
    :param link_item_dict: data
    :type link_item_dict: dict(str, ~unidown.plugins.data.link_item.LinkItem)
    """

    def __init__(self, version: Version, last_update: datetime, plugin_info: PluginInfo, link_item_dict: dict):
        self.plugin_info = plugin_info
        self.version = version
        self.last_update = last_update
        self.link_item_dict = link_item_dict

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.plugin_info == other.plugin_info and self.link_item_dict == other.link_item_dict and \
               self.version == other.version and self.last_update == other.last_update

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_protobuf(cls, proto: SaveStateProto):
        """
        Constructor from protobuf.

        :param proto: protobuf structure
        :type proto: ~unidown.plugins.data.protobuf.save_state_pb2.SaveStateProto
        :rtype: ~unidown.plugins.data.save_state.SaveState
        """
        data_dict = {}
        for key, link_item in proto.data.items():
            data_dict[key] = LinkItem.from_protobuf(link_item)
        try:
            version = Version(proto.version)
        except InvalidVersion:
            raise InvalidVersion('Plugin version is not PEP440 conform: {version}'.format(version=proto.version))
        return cls(version, Timestamp.ToDatetime(proto.last_update), PluginInfo.from_protobuf(proto.plugin_info),
                   data_dict)

    def to_protobuf(self):
        """
        Create protobuf item.

        :return: protobuf structure
        :rtype: ~unidown.plugins.data.protobuf.save_state_pb2.SaveStateProto
        """
        result = SaveStateProto()
        result.version = str(self.version)
        result.last_update.CopyFrom(datetime_to_timestamp(self.last_update))
        result.plugin_info.CopyFrom(self.plugin_info.to_protobuf())
        for key, link_item in self.link_item_dict.items():
            result.data[key].CopyFrom(link_item.to_protobuf())
        return result
