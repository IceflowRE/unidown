import re

from packaging.version import InvalidVersion, Version

from unidown.plugins.data.protobuf.plugin_info_pb2 import PluginInfoProto


class PluginInfo:
    """
    Information about the module. Those information will be saved into the save files as well.

    :param name: name
    :param version: version
    :param host: host name
    :raises ValueError: name is empty
    :raises ValueError: name contains spaces
    :raises ValueError: host is empty
    :raises InvalidVersion: version is not PEP440 conform

    :ivar name:
    :vartype name: str
    :ivar host:
    :vartype host: str
    :ivar version:
    :vartype version: ~packaging.version.Version
    """

    def __init__(self, name: str, version: str, host: str):
        if name is None or name == "":
            raise ValueError("Plugin name cannot be empty.")
        if re.search(r"\s", name):
            raise ValueError("Plugin name cannot contain spaces.")
        self.name = name

        if host is None or host == "":
            raise ValueError("Plugin host cannot be empty.")
        self.host = host

        try:
            self.version = Version(version)
        except InvalidVersion:
            raise InvalidVersion('Plugin version is not PEP440 conform: {version}'.format(version=version))

    @classmethod
    def from_protobuf(cls, proto: PluginInfoProto):
        """
        Constructor from protobuf.

        :param proto: protobuf
        :type proto: ~unidown.plugins.data.protobuf.plugin_info_pb2.PluginInfoProto
        :rtype: ~unidown.plugins.data.plugin_info.PluginInfo
        """
        return cls(proto.name, proto.version, proto.host)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and self.host == other.host and self.version == other.version

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.name + " - " + str(self.version) + " : " + self.host

    def to_protobuf(self):
        """
        Create protobuf item.

        :rtype: ~unidown.plugins.data.protobuf.link_item_pb2.PluginInfoProto
        """
        proto = PluginInfoProto()
        proto.name = self.name
        proto.version = str(self.version)
        proto.host = self.host
        return proto
