import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import certifi
import pkg_resources
import urllib3
from packaging.version import Version
from tqdm import tqdm
from urllib3.exceptions import HTTPError

from unidown import tools
from unidown.core.settings import Settings
from unidown.plugin.exceptions import PluginError
from unidown.plugin.link_item_dict import LinkItemDict
from unidown.plugin.plugin_info import PLUGIN_INFO_EMPTY, PluginInfo
from unidown.plugin.savestate import SaveState


# pylint: disable=R0904
class APlugin(ABC):  # noqa: PLR0904
    """
    Abstract class of a plugin. Provides all needed variables and methods.

    :param options: Parameters which can include optional parameters.
    :raises ~unidown.plugin.exceptions.PluginError: Can not create default plugin paths.
    """

    #: Meta information about the plugin.
    _INFO: PluginInfo = PLUGIN_INFO_EMPTY
    #: Savestate class to use.
    _SAVESTATE_CLS: type[SaveState] = SaveState

    def __init__(self, settings: Settings, options: Optional[dict[str, Any]] = None) -> None:
        if options is None:
            options = {}
        if self._INFO == PLUGIN_INFO_EMPTY:
            raise ValueError("info is not set.")

        #: If the tqdm progressbar should be disabled.
        self._disable_tqdm: bool = settings.disable_tqdm
        #: Use this for logging.
        self._log: logging.Logger = logging.getLogger(self._INFO.name)
        #: Number of simultaneous downloads.
        self._simul_downloads: int = settings.cores

        #: Path where the plugin can place all temporary data.
        self._temp_dir: Path = settings.temp_dir.joinpath(self.name)
        #: General download path of the plugin.
        self._download_dir: Path = settings.download_dir.joinpath(self.name)
        #: File which contains the latest savestate of the plugin.
        self._savestate_file: Path = settings.savestate_dir.joinpath(f"{self.name}_save.json")

        try:
            self._temp_dir.mkdir(parents=True, exist_ok=True)
            self._download_dir.mkdir(parents=True, exist_ok=True)
            self._savestate_file.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as ex:
            raise PluginError('Can not create default plugin paths, due to a permission error.') from ex

        # cached data
        #: Latest update time of the referencing data.
        self._last_update: datetime = datetime(1970, 1, 1)  # noqa: WPS432
        #: Referencing data.
        self._download_data: LinkItemDict = LinkItemDict()

        #: Savestate of the plugin.
        self._savestate: SaveState = self._SAVESTATE_CLS(self.info, self.last_update, LinkItemDict())

        #: The unit which will be displayed in the progress bar.
        self._unit: str = 'item'
        #: Downloader which will download the data.
        self._downloader: urllib3.HTTPSConnectionPool = urllib3.HTTPSConnectionPool(
            self.info.host, maxsize=self._simul_downloads, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()
        )

        # load options
        #: Options which the plugin uses internally, should be used for the given options at initialization.
        self._options: dict[str, Any] = options
        self._load_default_options()

    def __eq__(self, other: object) -> bool:
        """
        Two plugins are equal when having the same meta information.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.info == other.info

    def __ne__(self, other: object) -> bool:  # noqa: D105
        return not self.__eq__(other)

    def __hash__(self) -> int:  # noqa: D105
        return hash(self.info)

    @property
    def log(self) -> logging.Logger:
        """
        Plain getter.
        """
        return self._log

    @property
    def simul_downloads(self) -> int:
        """
        Plain getter.
        """
        return self._simul_downloads

    @property
    def info(self) -> PluginInfo:
        """
        Plain getter.
        """
        return self._INFO

    @property
    def host(self) -> str:
        """
        Plain getter.
        """
        return self._INFO.host

    @property
    def name(self) -> str:
        """
        Plain getter.
        """
        return self._INFO.name

    @property
    def version(self) -> Version:
        """
        Plain getter.
        """
        return self._INFO.version

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
    def savestate(self) -> SaveState:
        """
        Plain getter.
        """
        return self._savestate

    @property
    def last_update(self) -> datetime:
        """
        Plain getter.
        """
        return self._last_update

    @property
    def download_data(self) -> LinkItemDict:
        """
        Plain getter.
        """
        return self._download_data

    @property
    def unit(self) -> str:
        """
        Plain getter.
        """
        return self._unit

    @property
    def options(self) -> dict[str, Any]:
        """
        Plain getter.
        """
        return self._options

    def load_savestate(self) -> None:
        """
        Load the save of the plugin.

        :raises ~unidown.plugin.exceptions.PluginError: Broken savestate json.
        :raises ~unidown.plugin.exceptions.PluginError: Different savestate versions.
        :raises ~unidown.plugin.exceptions.PluginError: Different plugin versions.
        :raises ~unidown.plugin.exceptions.PluginError: Different plugin names.
        :raises ~unidown.plugin.exceptions.PluginError: Could not parse the json.
        """
        if not self._savestate_file.exists():
            self.log.info("No savestate file found.")
            return

        with self._savestate_file.open(encoding="utf8") as reader:
            try:
                savestate_json = json.loads(reader.read())
            except Exception as ex:
                raise PluginError(  # noqa: PLW0707
                    f"Broken savestate json. Please fix or delete this file (you may lose data in this case): {self._savestate_file}"
                ) from ex

        try:
            savestate = self._SAVESTATE_CLS.from_json(savestate_json)
        except Exception as ex2:
            raise PluginError(f"Could not load savestate from json {self._savestate_file}") from ex2
        del savestate_json  # noqa: WPS420
        savestate = self._SAVESTATE_CLS.upgrade(savestate)

        if savestate.plugin_info.name != self.info.name:
            raise PluginError(f"Save state plugin ({savestate.plugin_info.name}) does not match the current ({self.name}).")
        self._savestate = savestate

    def update_last_update(self) -> None:
        """
        Call this to update the latest update time. Calls :func:`~unidown.plugin.a_plugin.APlugin._create_last_update_time`.
        """
        self._last_update = self._create_last_update_time()

    def update_download_data(self) -> None:
        """
        Update the download links. Calls :func:`~unidown.plugin.a_plugin.APlugin._create_download_data`.
        """
        self._download_data = self._create_download_data()

    def download(self, link_items: LinkItemDict, folder: Path, desc: str, unit: str) -> None:
        """
        Download the given LinkItem dict from the plugins host, to the given path. Proceeded with multiple connections.
        :attr:`~unidown.plugin.a_plugin.APlugin._simul_downloads`. After
        :func:`~unidown.plugin.a_plugin.APlugin.check_download` is recommended.

        This function don't use an internal `link_item_dict`, `delay` or `folder` directly set in options or instance
        vars, because it can be used aside of the normal download routine inside the plugin itself for own things.
        As of this it still needs access to the logger, so a staticmethod is not possible.

        .. warning::

            The parameters may change in future versions. (e.g. change order and accept another host)

        :param link_items: Data which gets downloaded.
        :param folder: Target download folder.
        :param desc: Description of the progressbar.
        :param unit: Unit of the download, shown in the progressbar.
        """
        if not link_items:
            return

        job_list: list[Future] = []
        with ThreadPoolExecutor(max_workers=self._simul_downloads) as executor:
            for link, item in link_items.items():
                job: Future = executor.submit(self.download_as_file, link, folder.joinpath(item.name), self._options['delay'])
                job_list.append(job)

            pbar = tqdm(as_completed(job_list), total=len(job_list), desc=desc, unit=unit, mininterval=1, ncols=100, disable=self._disable_tqdm)
            for _ in pbar:  # noqa: WPS328
                pass  # noqa: WPS420

        for job in job_list:  # noqa: WPS440
            try:
                job.result()
            except HTTPError as ex:
                self.log.warning("Failed to download: %s", str(ex))

    def download_as_file(self, url: str, target_file: Path, delay: float = 0) -> str:
        """
        Download the given url to the given target folder.

        :param url: Link.
        :param target_file: Target file.
        :param delay: Delay after each download. Delay is in seconds.
        :return: Url.
        :raises ~urllib3.exceptions.HTTPError: Connection had an error.
        """
        if target_file.exists():
            new_name = target_file
            while new_name.exists():
                new_name = new_name.with_name(f"{new_name.stem}_r{''.join(new_name.suffixes)}")
            target_file.rename(new_name)
            self.log.critical("target file exists! renaming '%s' to '%s'", target_file, new_name)

        with self._downloader.request('GET', url, preload_content=False, retries=urllib3.util.retry.Retry(3)) as reader:
            if reader.status == 200:  # noqa: WPS432
                with target_file.open(mode='wb') as writer:
                    writer.write(reader.data)
            else:
                raise HTTPError(f"{url} | {reader.status}")

        if delay > 0:
            time.sleep(delay)

        return url

    def check_download(self, link_item_dict: LinkItemDict, folder: Path, log: bool = False) -> tuple[LinkItemDict, LinkItemDict]:
        """
        Check if the download of the given dict was successful. No proving if the content of the file is correct too.

        :param link_item_dict: Items to check.
        :param folder: Folder where the downloads are saved.
        :param log: Log lost items.
        :return: Succeed.
        """
        succeed = LinkItemDict({link: item for link, item in link_item_dict.items() if folder.joinpath(item.name).is_file()})
        failed = LinkItemDict({link: item for link, item in link_item_dict.items() if link not in succeed})

        if failed and log:
            for link, item in failed.items():
                self.log.warning("Not downloaded: %s%s - %s", self.info.host, link, item.name)

        return succeed, failed

    def update_savestate(self, new_items: LinkItemDict) -> None:
        """
        Update savestate.

        :param new_items: New items.
        """
        self._savestate.plugin_info = self.info
        self._savestate.last_update = self.last_update
        self._savestate.link_items.actualize(new_items)

    def save_savestate(self) -> None:
        """
        Save meta data about the downloaded things and the plugin to a file.
        """
        with self._savestate_file.open(mode='w', encoding="utf8") as writer:
            writer.write(json.dumps(self._savestate.to_json()))

    def clean_up(self) -> None:
        """
        Clean up for a module.
        Is deleting :attr:`~unidown.plugin.a_plugin.APlugin._temp_dir`.
        """
        self._downloader.close()
        tools.unlink_dir_rec(self._temp_dir)

    @abstractmethod
    def _create_last_update_time(self) -> datetime:
        """
        Get the newest update time from the referencing data.

        .. note:: Has to be implemented inside Plugin.

        :raises NotImplementedError: Abstract method.
        """
        raise NotImplementedError

    @abstractmethod
    def _create_download_data(self) -> LinkItemDict:
        """
        Get the download links in a specific format.

        .. note:: Has to be implemented inside Plugins.

        :raise NotImplementedError: Abstract method.
        """
        raise NotImplementedError

    def _load_default_options(self) -> None:
        """
        Load default options if they were not passed at creation.
        """
        delay: Any = self._options.get('delay')
        if delay is None:
            self._options['delay'] = 0
            self.log.warning("Plugin option 'delay' is missing. Using no delay.")
        elif not isinstance(delay, float):
            try:
                self._options['delay'] = float(delay)
            except ValueError:
                self._options['delay'] = 0
                self.log.warning("Plugin option 'delay' was not a float. Using no delay.")


def get_plugins() -> dict[str, pkg_resources.EntryPoint]:
    """
    Get all available plugins for unidown.

    :return: Plugin name list.
    """
    return {entry.name: entry for entry in pkg_resources.iter_entry_points('unidown.plugin')}
