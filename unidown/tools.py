"""
Different tools.
"""

from pathlib import Path

import pkg_resources


def unlink_dir_rec(path: Path) -> None:
    """
    Delete a folder recursive.

    :param path: Folder to delete.
    """
    if not path.exists() or not path.is_dir():
        return
    for sub in path.iterdir():
        if sub.is_dir():
            unlink_dir_rec(sub)
        else:
            sub.unlink()
    path.rmdir()


def print_plugin_list(plugins: dict[str, pkg_resources.EntryPoint]) -> None:
    """
    Print all registered plugins and checks if they can be loaded or not.

    :param plugins: Plugins name to entrypoint.
    """
    for name, entry_point in plugins.items():
        try:
            plugin_class = entry_point.load()
            # pylint: disable=W0212
            version = str(plugin_class._INFO.version)  # noqa: WPS437
            print(f"{name} (ok)\n    {version}")  # noqa: WPS421
        except Exception:  # pylint: disable=W0718
            print(f"{name} (failed)")  # noqa: WPS421
