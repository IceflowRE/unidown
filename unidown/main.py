"""
Entry into the program.
"""

import sys
import traceback
from argparse import ArgumentParser
from pathlib import Path

from unidown import dynamic_data, static_data
from unidown.core import manager


def main(args):
    """
    Entry point into the program. Gets the arguments from the console and proceed them with :class:`~argparse.ArgumentParser`.
    Returns if its success successful 0 else 1.
    """
    if sys.version_info[0] < 3 or sys.version_info[1] < 7:
        sys.exit('Only Python 3.7 or greater is supported. You are using:' + sys.version)

    parser = ArgumentParser(prog=static_data.LONG_NAME, description=static_data.DESCRIPTION)
    parser.add_argument('-v', '--version', action='version', version=(static_data.NAME + ' ' + static_data.VERSION))

    parser.add_argument('-p', '--plugin', action='append', nargs='+', dest='plugins', required=True, type=str,
                        metavar='name',
                        help='plugin to execute with given parameters')
    parser.add_argument('-m', '--main', dest='main_dir', default=dynamic_data.MAIN_DIR, type=Path, metavar='path',
                        help='main directory where all files will be created (default: %(default)s)')
    parser.add_argument('-o', '--output', dest='logfile', default=dynamic_data.LOGFILE_PATH, type=Path, metavar='path',
                        help='log filepath relativ to the main dir (default: %(default)s)')
    parser.add_argument('-l', '--log', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default=dynamic_data.LOG_LEVEL, help='set the logging level (default: %(default)s)')

    args = parser.parse_args(args)
    try:
        manager.init(Path(args.main_dir), Path(args.logfile), args.log_level)
    except PermissionError:
        print('Cant create needed folders. Make sure you have write permissions.')
        sys.exit(1)
    except FileExistsError as ex:
        print(ex)
        sys.exit(1)
    except Exception as ex:
        print('Something went wrong: ' + traceback.format_exc(ex.__traceback__))
        sys.exit(1)
    manager.check_update()
    for plugin in args.plugins:
        manager.run(plugin[0], plugin[1:])
    manager.shutdown()
    sys.exit(0)
