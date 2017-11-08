import re

from unidown.plugins.data.protobuf.plugin_info_pb2 import PluginInfoProto


class PluginInfo:
    """
    Information about the module. Those information will be saved into the save files as well.
    """

    def __init__(self, name: str, version: str, host: str):
        """
        Constructor.
        :param name: name
        :param version: version
        :param host: host name
        :raise: ValueError
        """
        if name is None or name == "":
            raise ValueError("Name cannot be empty.")
        if re.search(r"\s", name):
            raise ValueError("Name cannot contain spaces.")
        self.name = name

        if host is None or host == "":
            raise ValueError("Host cannot be empty.")
        self.host = host

        ver_split = version.split('.')
        for item in ver_split:
            if not item.isdigit():
                raise ValueError("Version can only contains digits splitted by a dot.")  # TODO: allow chars
        self.version = version

    @classmethod
    def from_protobuf(cls, proto: PluginInfoProto):
        """
        Constructor from protobuf.
        :param proto: protobuf
        """
        return cls(proto.name, proto.version, proto.host)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and self.host == other.host and self.version == other.version

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name + " - " + self.version + " : " + self.host

    def to_protobuf(self):
        """
        Create protobuf item.
        :return: protobuf
        """
        proto = PluginInfoProto()
        proto.name = self.name
        proto.version = self.version
        proto.host = self.host
        return proto
