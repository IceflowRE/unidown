"""
Entry into the program.
"""
import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Optional

from unidown import meta, tools
from unidown.core import manager
from unidown.core.settings import Settings
from unidown.plugin.a_plugin import get_plugins


class PluginListAction(argparse.Action):
    """
    Lists all plugins which are available. Extension for :class:`~argparse.ArgumentParser`.
    """

    def __init__(self, option_strings: Sequence[str], dest: str, **kwargs) -> None:
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(  # noqa: D102
            self, parser: argparse.ArgumentParser, namespace: argparse.Namespace, values: str | Sequence[Any] | None, option_string: str | None = None
    ) -> None:
        tools.print_plugin_list(get_plugins())
        parser.exit()


def main(argv: Optional[list[str]] = None) -> None:  # noqa: WPS213
    """
    Entry point into the program. Gets the arguments from the console and proceed them with :class:`~argparse.ArgumentParser`.
    Returns if its success successful 0 else 1.
    """
    if sys.version_info < (3, 10):
        sys.exit('Only Python 3.10 or greater is supported. You are using:' + sys.version)  # noqa: WPS336

    if argv is None:
        argv = sys.argv[1:]

    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog=meta.LONG_NAME, description=meta.DESCRIPTION)
    parser.add_argument('-v', '--version', action='version', version=f"{meta.NAME} {meta.VERSION}")
    parser.add_argument('--list-plugins', action=PluginListAction, help="show plugin list and exit")

    parser.add_argument('-p', '--plugin', dest='plugin', default="", type=str, required=True, metavar='name', help='plugin to execute')
    parser.add_argument(  # noqa: WPS317
        '-o', '--option', action='append', nargs='+', dest='options', type=str, metavar='option',
        help='options passed to the plugin, e.g. `-o username=South American coati -o password=Nasua Nasua`'
    )
    parser.add_argument(  # noqa: WPS317, WPS437
        '-r', '--root', dest='root_dir', default=None, type=str, metavar='path',
        help='main directory where all files will be created (default: %(default)s)'  # noqa: WPS323
    )
    parser.add_argument(
        '--logfile', dest='logfile', default=None, type=str, metavar='path', help='log filepath relative to the main dir (default: %(default)s)'  # noqa: WPS323
    )
    parser.add_argument(  # noqa: WPS317
        '-l', '--log', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
        help='set the logging level (default: %(default)s)'  # noqa: WPS323
    )

    args = parser.parse_args(argv)
    try:
        root_dir: Path = args.root_dir
        if args.root_dir is not None:
            root_dir = Path(args.root_dir)
        log_file: Path = args.logfile
        if args.logfile is not None:
            log_file = Path(args.logfile)
        settings: Settings = Settings(root_dir, log_file, args.log_level)
        settings.mkdir()
        manager.init_logging(settings)
    except PermissionError:
        logging.critical('Cant create needed folders. Make sure you have write permissions.')
        sys.exit(1)
    except FileExistsError:
        logging.exception("")
        sys.exit(1)
    except Exception:  # pylint: disable=W0718
        logging.exception("Something went wrong")
        sys.exit(1)
    manager.check_update()
    manager.run(settings, args.plugin, args.options)
    manager.shutdown()
    sys.exit(0)
