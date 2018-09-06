"""
Different tools.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict

import pkg_resources
from google.protobuf.timestamp_pb2 import Timestamp


def delete_dir_rec(path: Path):
    """
    Delete a folder recursive.

    :param path: folder to deleted
    :type path: ~pathlib.Path
    """
    if not path.exists() or not path.is_dir():
        return
    for sub in path.iterdir():
        if sub.is_dir():
            delete_dir_rec(sub)
        else:
            sub.unlink()
    path.rmdir()


def create_dir_rec(path: Path):
    """
    Create a folder recursive.

    :param path: path
    :type path: ~pathlib.Path
    """
    if not path.exists():
        Path.mkdir(path, parents=True, exist_ok=True)


def datetime_to_timestamp(time: datetime) -> Timestamp:
    """
    Convert datetime to protobuf.timestamp.

    :param time: time
    :type time: ~datetime.datetime
    :return: protobuf.timestamp
    :rtype: ~google.protobuf.timestamp_pb2.Timestamp
    """
    protime = Timestamp()
    protime.FromDatetime(time)
    return protime


def print_plugin_list(plugins: Dict[str, pkg_resources.EntryPoint]):
    """
    Prints all registered plugins and checks if they can be loaded or not.

    :param plugins: plugins
    :type plugins: Dict[str, ~pkg_resources.EntryPoint]
    """
    for trigger, entry_point in plugins.items():
        try:
            plugin_class = entry_point.load()
            version = str(plugin_class._info.version)
            print(
                f"{trigger} (ok)\n"
                f"    {version}"
            )
        except Exception:
            print(
                f"{trigger} (failed)"
            )
