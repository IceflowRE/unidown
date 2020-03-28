import multiprocessing
from pathlib import Path


class Settings:
    """
    :ivar _root_dir: root path
    :ivar temp_dir: temporary main path, here are the sub folders for every plugin
    :ivar download_dir: download main path, here are the sub folders for every plugin
    :ivar savestate_dir: savestates main path, here are the sub folders for every plugin
    :ivar log_file: log file of the program
    :ivar available_plugins: available plugins which are found at starting the program, name -> EntryPoint
    :ivar using_cores: how many _cores should be used
    :ivar _log_level: log level
    :ivar _disable_tqdm: if the console progress bar is disabled

    :param root_dir: root dir
    :param log_file: log file
    """

    def __init__(self, root_dir: Path = None, log_file: Path = None, log_level: str = 'INFO'):
        if root_dir is None:
            root_dir = Path('./')
        if log_file is None:
            log_file = root_dir.joinpath(Path('unidown.log'))
        self._root_dir: Path = root_dir
        self._temp_dir: Path = self._root_dir.joinpath(Path('temp/'))
        self._download_dir: Path = self._root_dir.joinpath(Path('downloads/'))
        self._savestate_dir: Path = self._root_dir.joinpath(Path('savestates/'))
        self._log_file: Path = log_file
        self._cores = min(4, max(1, multiprocessing.cpu_count() - 1))
        self._log_level = log_level
        self._disable_tqdm = False

    def mkdir(self):
        """
        Create all base directories.
        """
        self._root_dir.mkdir(parents=True, exist_ok=True)
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._download_dir.mkdir(parents=True, exist_ok=True)
        self._savestate_dir.mkdir(parents=True, exist_ok=True)

    def check_dirs(self):
        """
        Check the directories if they exist.

        :raises FileExistsError: if a file exists but is not a directory
        """
        dirs = [self._root_dir, self._temp_dir, self._download_dir, self._savestate_dir]
        for directory in dirs:
            if directory.exists() and not directory.is_dir():
                raise FileExistsError(str(directory.resolve()) + " cannot be used as a directory.")

    @property
    def root_dir(self) -> Path:
        """
        Plain getter.
        """
        return self._root_dir

    @property
    def temp_dir(self) -> Path:
        """
        Plain getter.
        """
        return self._temp_dir

    @property
    def download_dir(self) -> Path:
        """
        Plain getter.
        """
        return self._download_dir

    @property
    def savestate_dir(self) -> Path:
        """
        Plain getter.
        """
        return self._savestate_dir

    @property
    def log_file(self) -> Path:
        """
        Plain getter.
        """
        return self._log_file

    @property
    def cores(self) -> int:
        """
        Plain getter.
        """
        return self._cores

    @property
    def log_level(self) -> str:
        """
        Plain getter.
        """
        return self._log_level

    @property
    def disable_tqdm(self) -> bool:
        """
        Plain getter.
        """
        return self._disable_tqdm
