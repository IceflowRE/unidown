import multiprocessing
from pathlib import Path
from typing import Optional


class Settings:
    """
    Settings.

    :param root_dir: root dir
    :param log_file: log file
    """

    def __init__(self, root_dir: Optional[Path] = None, log_file: Optional[Path] = None, log_level: str = 'INFO') -> None:
        if root_dir is None:
            root_dir = Path('./')
        if log_file is None:
            log_file = root_dir.joinpath(Path('unidown.log'))
        #: Root path.
        self._root_dir: Path = root_dir
        #: Temporary main path, here are the sub folders for every plugin.
        self._temp_dir: Path = self._root_dir.joinpath(Path('temp/'))
        #: Download main path, here are the sub folders for every plugin.
        self._download_dir: Path = self._root_dir.joinpath(Path('downloads/'))
        #: Savestates main path, here are the sub folders for every plugin.
        self._savestate_dir: Path = self._root_dir.joinpath(Path('savestates/'))
        #: Log file of the program.
        self._log_file: Path = log_file
        #: Number of cores to be used.
        self._cores = min(4, max(1, multiprocessing.cpu_count() - 1))
        #: Log level.
        self._log_level = log_level
        #: Disable console progress bar.
        self._disable_tqdm = False

    def mkdir(self) -> None:
        """
        Create all base directories.
        """
        self._root_dir.mkdir(parents=True, exist_ok=True)
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._download_dir.mkdir(parents=True, exist_ok=True)
        self._savestate_dir.mkdir(parents=True, exist_ok=True)

    def check_dirs(self) -> None:
        """
        Check the directories if they exist.

        :raises FileExistsError: if a file exists but is not a directory
        """
        dirs = [self._root_dir, self._temp_dir, self._download_dir, self._savestate_dir]
        for directory in dirs:
            if directory.exists() and not directory.is_dir():
                raise FileExistsError(f"{directory.resolve()} cannot be used as a directory.")

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
