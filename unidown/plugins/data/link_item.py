from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

from unidown.plugins.data.protobuf.link_item_pb2 import LinkItemProto
from unidown.tools.tools import datetime_to_timestamp


class LinkItem:
    """
    Item which represents the data, who need to be downloaded. Has a name and an update time.

    :param name: name
    :type name: str
    :param time: update time
    :type time: ~datetime.datetime

    :ivar _name: name of the item
    :vartype _name: str
    :ivar _time: time of the item
    :vartype _time: ~datetime.datetime
    """

    def __init__(self, name, time: datetime):
        self._name = name
        self._time = time

    @classmethod
    def from_protobuf(cls, proto: LinkItemProto):
        """
        Constructor from protobuf.

        :param proto: protobuf structure
        :type proto: ~unidown.plugins.data.protobuf.link_item_pb2.LinkItemProto
        :rtype: ~unidown.plugins.data.link_item.LinkItem
        """
        return cls(proto.name, Timestamp.ToDatetime(proto.time))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._name == other.name and self._time == other.time

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '(' + str(self._name) + ', ' + str(self._time) + ')'

    @property
    def name(self):
        """
        :py:attr:`~unidown.plugins.data.link_item.LinkItem._name`.

        :rtype: str
        """
        return self._name

    @property
    def time(self):
        """
        :py:attr:`~unidown.plugins.data.link_item.LinkItem._time`.

        :rtype: ~datetime.datetime
        """
        return self._time

    def to_protobuf(self):
        """
        Create protobuf item.

        :return: protobuf structure
        :rtype: ~unidown.plugins.data.protobuf.link_item_pb2.LinkItemProto
        """
        result = LinkItemProto()
        result.name = self._name
        result.time.CopyFrom(datetime_to_timestamp(self._time))
        return result
