from __future__ import annotations

from typing import Self

from packaging.version import InvalidVersion, Version


class PluginInfo:
    """
    Information about the module. This information will be saved into the save files as well.

    .. warning:

        Parameters may change in the future.

    :param name: Name of the plugin.
    :param version: Version, PEP440 conform.
    :param host: Host url of the main data.
    :raises ValueError: Name is empty.
    :raises ValueError: Host is empty.
    :raises ~packaging.version.InvalidVersion: Version is not PEP440 conform.
    """

    def __init__(self, name: str, version: str, host: str) -> None:
        if name is None or not name:
            raise ValueError("Plugin parameter 'name' cannot be empty.")
        if host is None or not host:
            raise ValueError("Plugin parameter 'host' cannot be empty.")
        #: Name of the plugin.
        self.name: str = name
        #: Host url of the main data.
        self.host: str = host

        try:
            #: Plugin version.
            self.version: Version = Version(version)
        except InvalidVersion as ex:
            raise InvalidVersion(f"Plugin version is not PEP440 conform: {version}") from ex

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """
        Construct from json dict.

        :param data: Json data as dict.
        :return: Plugin info.
        :raises ValueError: Name is missing.
        :raises ValueError: Version is missing.
        :raises ValueError: Host is missing.
        """
        if 'name' not in data:
            raise ValueError("name is missing")
        if 'version' not in data:
            raise ValueError("version is missing")
        if 'host' not in data:
            raise ValueError("host is missing")
        return cls(data['name'], data['version'], data['host'])

    def __eq__(self, other: object) -> bool:  # noqa: D105
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name and self.host == other.host and self.version == other.version

    def __ne__(self, other: object) -> bool:  # noqa: D105
        return not self.__eq__(other)

    def __hash__(self) -> int:  # noqa: D105
        return hash((self.name, self.host, self.version))

    def __str__(self) -> str:  # noqa: D105
        return f"{self.name} - {self.version} : {self.host}"

    def to_json(self) -> dict:
        """
        Create json data.

        :return: Json dictionary.
        """
        return {'name': self.name, 'version': str(self.version), 'host': self.host}


PLUGIN_INFO_EMPTY: PluginInfo = PluginInfo("empty", "0.0.0", "empty")
