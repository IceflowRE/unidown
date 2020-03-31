"""
Different tools.
"""

from pathlib import Path
from typing import Dict

import pkg_resources


def unlink_dir_rec(path: Path):
    """
    Delete a folder recursive.

    :param path: folder to deleted
    """
    if not path.exists() or not path.is_dir():
        return
    for sub in path.iterdir():
        if sub.is_dir():
            unlink_dir_rec(sub)
        else:
            sub.unlink()
    path.rmdir()


def print_plugin_list(plugins: Dict[str, pkg_resources.EntryPoint]):
    """
    Prints all registered plugins and checks if they can be loaded or not.

    :param plugins: plugins name to entrypoint
    """
    for name, entry_point in plugins.items():
        try:
            plugin_class = entry_point.load()
            version = str(plugin_class._info.version)
            print(
                f"{name} (ok)\n"
                f"    {version}"
            )
        except Exception:
            print(f"{name} (failed)")
