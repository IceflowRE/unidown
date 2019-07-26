from __future__ import annotations

from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

from unidown.plugin.protobuf.link_item_pb2 import LinkItemProto
from unidown.tools import datetime_to_timestamp


class LinkItem:
    """
    Item which represents the data, who need to be downloaded. Has a name and an update time.

    :param name: name
    :param time: update time
    :raises ValueError: name cannot be empty or None
    :raises ValueError: time cannot be empty or None

    :ivar _name: name of the item
    :vartype _name: str
    :ivar _time: time of the item
    :vartype _time: ~datetime.datetime
    """

    def __init__(self, name: str, time: datetime):
        self._name = self.name = name
        self._time = self.time = time

    @classmethod
    def from_protobuf(cls, proto: LinkItemProto) -> LinkItem:
        """
        Constructor from protobuf.

        :param proto: protobuf structure
        :return: the LinkItem
        :raises ValueError: name of LinkItem does not exist inside the protobuf or is empty
        """
        if proto.name == '':
            raise ValueError("name of LinkItem does not exist or is empty inside the protobuf.")
        return cls(proto.name, Timestamp.ToDatetime(proto.time))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._name == other._name and self._time == other._time

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return '(' + str(self._name) + ', ' + str(self._time) + ')'

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if name is None or name == '':
            raise ValueError("name cannot be empty or None.")
        self._name = name

    @property
    def time(self) -> datetime:
        return self._time

    @time.setter
    def time(self, time: datetime):
        if time is None:
            raise ValueError("time cannot be None.")
        self._time = time

    def to_protobuf(self) -> LinkItemProto:
        """
        Create protobuf item.

        :return: protobuf structure
        """
        result = LinkItemProto()
        result.name = self._name
        result.time.CopyFrom(datetime_to_timestamp(self._time))
        return result
