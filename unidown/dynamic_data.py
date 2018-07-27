"""
Dynamical variables, which will be initialized and can be changed while runtime or needs third party libraries (like pathlib.Path).
"""
from pathlib import Path

from packaging.version import Version

# paths
#: main path
MAIN_DIR = Path('./')
#: temporary main path, here are the sub folders for every plugin
TEMP_DIR = MAIN_DIR.joinpath(Path('temp/'))
#: download main path, here are the sub folders for every plugin
DOWNLOAD_DIR = MAIN_DIR.joinpath(Path('downloads/'))
#: savestates main path, here are the sub folders for every plugin
SAVESTAT_DIR = MAIN_DIR.joinpath(Path('savestates/'))
#: log file of the program
LOGFILE_PATH = MAIN_DIR.joinpath(Path('UniDown.log'))

#: available plugins which are found at starting the program, name -> EntryPoint
AVAIL_PLUGINS = {}

#: how many core shoud be used
USING_CORES = 1
#: log level
LOG_LEVEL = 'INFO'
#: if the console progress bar is disabled
DISABLE_TQDM = False

#: current savestate version which will be used **Do not edit**
SAVE_STATE_VERSION = Version('1')


# ===========================


def init_dirs(main_dir: Path, logfilepath: Path):
    """
    Initialize the main directories.

    :param main_dir: main directory
    :type main_dir: ~pathlib.Path
    :param logfilepath: log file
    :type logfilepath: ~pathlib.Path
    """
    global MAIN_DIR, TEMP_DIR, DOWNLOAD_DIR, SAVESTAT_DIR, LOGFILE_PATH
    MAIN_DIR = main_dir
    TEMP_DIR = MAIN_DIR.joinpath(Path('temp/'))
    DOWNLOAD_DIR = MAIN_DIR.joinpath(Path('downloads/'))
    SAVESTAT_DIR = MAIN_DIR.joinpath(Path('savestates/'))
    LOGFILE_PATH = MAIN_DIR.joinpath(logfilepath)


def reset():
    """
    Reset all dynamic variables to the default values.
    """
    global MAIN_DIR, TEMP_DIR, DOWNLOAD_DIR, SAVESTAT_DIR, LOGFILE_PATH, USING_CORES, LOG_LEVEL, DISABLE_TQDM, \
        SAVE_STATE_VERSION
    MAIN_DIR = Path('./')
    TEMP_DIR = MAIN_DIR.joinpath(Path('temp/'))
    DOWNLOAD_DIR = MAIN_DIR.joinpath(Path('downloads/'))
    SAVESTAT_DIR = MAIN_DIR.joinpath(Path('savestates/'))
    LOGFILE_PATH = MAIN_DIR.joinpath(Path('UniDown.log'))

    USING_CORES = 1
    LOG_LEVEL = 'INFO'
    DISABLE_TQDM = False

    SAVE_STATE_VERSION = Version('1')


def check_dirs():
    """
    Check the directories if they exist.

    :raises FileExistsError: if a file exists but is not a directory
    """
    dirs = [MAIN_DIR, TEMP_DIR, DOWNLOAD_DIR, SAVESTAT_DIR]
    for directory in dirs:
        if directory.exists() and not directory.is_dir():
            raise FileExistsError(str(directory.resolve()) + " cannot be used as a directory.")
