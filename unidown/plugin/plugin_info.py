from __future__ import annotations

from packaging.version import InvalidVersion, Version


class PluginInfo:
    """
    .. warning:

        Parameters may change in the future.

    Information about the module. Those information will be saved into the save files as well.

    :param name: the name of the plugin
    :param version: version, PEP440 conform
    :param host: host url of the main data
    :raises ValueError: name is empty
    :raises ValueError: host is empty
    :raises ~packaging.version.InvalidVersion: version is not PEP440 conform

    :ivar name: name
    :ivar host: host url of the main data
    :ivar version: plugin version
    """

    def __init__(self, name: str, version: str, host: str):
        if name is None or name == "":
            raise ValueError("Plugin name cannot be empty.")
        elif host is None or host == "":
            raise ValueError("Plugin host cannot be empty.")
        self.name: str = name
        self.host: str = host

        try:
            self.version: Version = Version(version)
        except InvalidVersion:
            raise InvalidVersion(f"Plugin version is not PEP440 conform: {version}")

    @classmethod
    def from_json(cls, data: dict) -> PluginInfo:
        """
        Constructor from json dict.

        :param data: json data as dict
        :return: the PluginInfo
        :raises ValueError: name is missing
        :raises ValueError: version is missing
        :raises ValueError: host is missing
        """
        if 'name' not in data:
            raise ValueError("name is missing")
        elif 'version' not in data:
            raise ValueError("version is missing")
        elif 'host' not in data:
            raise ValueError("host is missing")
        return cls(data['name'], data['version'], data['host'])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and self.host == other.host and self.version == other.version

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return self.name + " - " + str(self.version) + " : " + self.host

    def to_json(self) -> dict:
        """
        Create json data.

        :return: json dictionary
        """
        return {'name': self.name, 'version': str(self.version), 'host': self.host}
