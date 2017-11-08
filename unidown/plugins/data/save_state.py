from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

from unidown.plugins.data.link_item import LinkItem
from unidown.plugins.data.plugin_info import PluginInfo
from unidown.plugins.data.protobuf.save_state_pb2 import SaveStateProto
from unidown.tools.tools import datetime_to_timestamp


class SaveState:
    """
    Savestate of a module. Includes info about the module, savestate version, update time of the containing data and the
    data itself as a dict of link: LinkItem.
    """

    def __init__(self, save_state_version, last_update: datetime, plugin_info: PluginInfo, link: dict):
        self.plugin_info = plugin_info
        self.save_state_version = save_state_version
        self.last_update = last_update
        self.link_linkitem = link

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.plugin_info == other.plugin_info and self.save_state_version == other.save_state_version and \
               self.last_update == other.last_update and self.link_linkitem == other.link_linkitem

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_protobuf(cls, proto):
        """
        Constructor from protobuf.
        :param proto: protobuf
        """
        data_dict = {}
        for key, link_item in proto.data.items():
            data_dict[key] = LinkItem.from_protobuf(link_item)
        return cls(proto.save_state_version, Timestamp.ToDatetime(proto.last_update),
                   PluginInfo.from_protobuf(proto.plugin_info), data_dict)

    def to_protobuf(self):
        """
        Create protobuf item.
        :return: protobuf
        """
        result = SaveStateProto()
        result.save_state_version = self.save_state_version
        result.last_update.CopyFrom(datetime_to_timestamp(self.last_update))
        result.plugin_info.CopyFrom(self.plugin_info.to_protobuf())
        for key, link_item in self.link_linkitem.items():
            result.data[key].CopyFrom(link_item.to_protobuf())
        return result
