"""
Entry into the program.
"""
import argparse
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

from unidown import static_data, tools
from unidown.core import manager
from unidown.core.settings import Settings
from unidown.plugin.a_plugin import APlugin


class PluginListAction(argparse.Action):
    """
    Lists all plugins which are available. Extension for the argparser.
    """

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        tools.print_plugin_list(APlugin.get_plugins())
        parser.exit()


def main(argv=None):
    """
    Entry point into the program. Gets the arguments from the console and proceed them with :class:`~argparse.ArgumentParser`.
    Returns if its success successful 0 else 1.
    """
    if sys.version_info[0] < 3 or sys.version_info[1] < 8:
        sys.exit('Only Python 3.8 or greater is supported. You are using:' + sys.version)

    if argv is None:
        argv = sys.argv[1:]

    parser = ArgumentParser(prog=static_data.LONG_NAME, description=static_data.DESCRIPTION)
    parser.add_argument('-v', '--version', action='version', version=f"{static_data.NAME} {static_data.VERSION}")
    parser.add_argument('--list-plugins', action=PluginListAction, help="show plugin list and exit")

    parser.add_argument('-p', '--plugin', dest='plugin', default="", type=str, required=True, metavar='name',
                        help='plugin to execute')
    parser.add_argument('-o', '--option', action='append', nargs='+', dest='options', type=str, metavar='option',
                        help='options passed to the plugin, e.g. `-o username=South American coati -o password=Nasua Nasua`')
    parser.add_argument('-r', '--root', dest='root_dir', default=None, type=str, metavar='path',
                        help='main directory where all files will be created (default: %(default)s)')
    parser.add_argument('--logfile', dest='logfile', default=None, type=str, metavar='path',
                        help='log filepath relativ to the main dir (default: %(default)s)')
    parser.add_argument('-l', '--log', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        help='set the logging level (default: %(default)s)')

    args = parser.parse_args(argv)
    try:
        root_dir = args.root_dir
        if args.root_dir is not None:
            root_dir = Path(args.root_dir)
        log_file = args.logfile
        if args.logfile is not None:
            log_file = Path(args.logfile)
        settings = Settings(root_dir, log_file, args.log_level)
        settings.mkdir()
        manager.init_logging(settings)
    except PermissionError:
        logging.critical('Cant create needed folders. Make sure you have write permissions.')
        sys.exit(1)
    except FileExistsError:
        logging.exception("")
        sys.exit(1)
    except Exception:
        logging.exception("Something went wrong")
        sys.exit(1)
    manager.check_update()
    manager.run(settings, args.plugin, args.options)
    manager.shutdown()
    sys.exit(0)
