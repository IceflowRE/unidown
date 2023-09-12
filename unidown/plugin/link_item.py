from __future__ import annotations

from datetime import datetime
from typing import Self


class LinkItem:
    """
    Item which represents the data, who need to be downloaded. Has a name and an update time.

    :param name: name
    :param time: update time
    :raises ValueError: name cannot be empty or None
    :raises ValueError: time cannot be empty or None
    """

    #: Time format to use.
    TIME_FORMAT: str = "%Y%m%dT%H%M%S.%fZ"  # noqa: WPS323

    def __init__(self, name: str, time: datetime) -> None:
        #: Name of the item.
        self._name: str = ""
        #: Time of the item.
        self._time: datetime = datetime(1970, 1, 1)  # noqa: WPS432
        self.name = name
        self.time = time

    @classmethod
    def from_json(cls, data: dict) -> Self:
        """
        Construct from json dict.

        :param data: Json data as dict.
        :return: LinkItem.
        :raises ValueError: Missing parameter.
        """
        if 'name' not in data:
            raise ValueError("name is missing")
        if 'time' not in data:
            raise ValueError("time is missing")
        return cls(data['name'], datetime.strptime(data['time'], LinkItem.TIME_FORMAT))

    def __eq__(self, other: object) -> bool:  # noqa: D105
        if not isinstance(other, self.__class__):
            return False
        return self._name == other._name and self._time == other._time  # noqa: WPS437

    def __ne__(self, other: object) -> bool:  # noqa: D105
        return not self.__eq__(other)

    def __hash__(self) -> int:  # noqa: D105
        return hash((self._name, self._time))

    def __repr__(self) -> str:  # noqa: D105
        return self.__str__()

    def __str__(self) -> str:  # noqa: D105
        return f"{self._name}, {self._time}"

    @property
    def name(self) -> str:
        """
        Plain getter.
        """
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """
        Set item name.

        :raises ValueError: Name cannot be empty or None.
        """
        if name is None or not name:
            raise ValueError("name cannot be empty or None.")
        self._name = name

    @property
    def time(self) -> datetime:
        """
        Plain getter.
        """
        return self._time

    @time.setter
    def time(self, time: datetime) -> None:
        """
        Set the item time.

        :raises ValueError: Time cannot be None.
        """
        if time is None:
            raise ValueError("time cannot be None.")
        self._time = time

    def to_json(self) -> dict:
        """
        Create json data.

        :return: Json dictionary.
        """
        return {'name': self._name, 'time': self._time.strftime(LinkItem.TIME_FORMAT)}
