import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import certifi
import pkg_resources
import urllib3
import urllib3.util
from packaging.version import Version
from tqdm import tqdm
from urllib3.exceptions import HTTPError

from unidown import tools
from unidown.core.settings import Settings
from unidown.plugin.exceptions import PluginException
from unidown.plugin.link_item_dict import LinkItemDict
from unidown.plugin.plugin_info import PluginInfo
from unidown.plugin.savestate import SaveState


class APlugin(ABC):
    """
    Abstract class of a plugin. Provides all needed variables and methods.

    :param options: parameters which can included optional parameters
    :raises ~unidown.plugin.exceptions.PluginException: can not create default plugin paths

    :cvar _info: information about the plugin
    :cvar _savestate_cls: savestate class to use
    :ivar _disable_tqdm: if the tqdm progressbar should be disabled **| do not edit**
    :ivar _log: use this for logging **| do not edit**
    :ivar _simul_downloads: number of simultaneous downloads
    :ivar _temp_dir: path where the plugin can place all temporary data **| do not edit**
    :ivar _download_dir: general download path of the plugin **| do not edit**
    :ivar _savestate_file: file which contains the latest savestate of the plugin **| do not edit**
    :ivar _last_update: latest update time of the referencing data **| do not edit**
    :ivar _unit: the thing which should be downloaded, may be displayed in the progress bar
    :ivar _download_data: referencing data **| do not edit**
    :ivar _downloader: downloader which will download the data **| do not edit**
    :ivar _savestate: savestate of the plugin
    :ivar _options: options which the plugin uses internal, should be used for the given options at init
    """
    _info: PluginInfo = None
    _savestate_cls = SaveState

    def __init__(self, settings: Settings, options: Dict[str, Any] = None):
        if options is None:
            options = {}
        if self._info is None:
            raise ValueError("info is not set.")

        self._disable_tqdm = settings.disable_tqdm
        self._log: logging.Logger = logging.getLogger(self._info.name)
        self._simul_downloads: int = settings.cores

        self._temp_dir: Path = settings.temp_dir.joinpath(self.name)
        self._download_dir: Path = settings.download_dir.joinpath(self.name)
        self._savestate_file: Path = settings.savestate_dir.joinpath(self.name + '_save.json')

        try:
            self._temp_dir.mkdir(parents=True, exist_ok=True)
            self._download_dir.mkdir(parents=True, exist_ok=True)
            self._savestate_file.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise PluginException('Can not create default plugin paths, due to a permission error.')

        # cached data
        self._last_update: datetime = datetime(1970, 1, 1)
        self._download_data: LinkItemDict = LinkItemDict()

        self._savestate: SaveState = self._savestate_cls(self.info, self.last_update, LinkItemDict())

        self._unit: str = 'item'
        self._downloader: urllib3.HTTPSConnectionPool = urllib3.HTTPSConnectionPool(
            self.info.host, maxsize=self._simul_downloads, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()
        )

        # load options
        self._options: Dict[str, Any] = options
        self._load_default_options()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.info == other.info

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

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
        return self._info

    @property
    def host(self) -> str:
        """
        Plain getter.
        """
        return self._info.host

    @property
    def name(self) -> str:
        """
        Plain getter.
        """
        return self._info.name

    @property
    def version(self) -> Version:
        """
        Plain getter.
        """
        return self._info.version

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
    def savestate(self):
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
    def options(self) -> Dict[str, Any]:
        """
        Plain getter.
        """
        return self._options

    def load_savestate(self):
        """
        Load the save of the plugin.

        :raises ~unidown.plugin.exceptions.PluginException: broken savestate json
        :raises ~unidown.plugin.exceptions.PluginException: different savestate versions
        :raises ~unidown.plugin.exceptions.PluginException: different plugin versions
        :raises ~unidown.plugin.exceptions.PluginException: different plugin names
        :raises ~unidown.plugin.exceptions.PluginException: could not parse the json
        """
        if not self._savestate_file.exists():
            self.log.info("No savestate file found.")
            return

        with self._savestate_file.open(encoding="utf8") as reader:
            try:
                savestate_json = json.loads(reader.read())
            except Exception:
                raise PluginException(f"Broken savestate json. Please fix or delete this file (you may lose data in this case): {self._savestate_file}")

        try:
            savestate = self._savestate_cls.from_json(savestate_json)
        except Exception as ex:
            raise PluginException(f"Could not load savestate from json {self._savestate_file}: {ex}")
        else:
            del savestate_json
        savestate = self._savestate_cls.upgrade(savestate)

        if savestate.plugin_info.name != self.info.name:
            raise PluginException(
                "Save state plugin ({name}) does not match the current ({cur_name}).".format(name=savestate.plugin_info.name, cur_name=self.name))
        self._savestate = savestate

    @abstractmethod
    def _create_last_update_time(self) -> datetime:
        """
        Get the newest update time from the referencing data.
        **Has to be implemented inside Plugins.**

        :raises NotImplementedError: abstract method
        """
        raise NotImplementedError

    def update_last_update(self):
        """
        Call this to update the latest update time. Calls :func:`~unidown.plugin.a_plugin.APlugin._create_last_update_time`.
        """
        self._last_update = self._create_last_update_time()

    @abstractmethod
    def _create_download_data(self) -> LinkItemDict:
        """
        Get the download links in a specific format.
        **Has to be implemented inside Plugins.**

        :raises NotImplementedError: abstract method
        """
        raise NotImplementedError

    def update_download_data(self):
        """
        Update the download links. Calls :func:`~unidown.plugin.a_plugin.APlugin._create_download_data`.
        """
        self._download_data = self._create_download_data()

    def download(self, link_items: LinkItemDict, folder: Path, desc: str, unit: str):
        """
        .. warning::

            The parameters may change in future versions. (e.g. change order and accept another host)

        Download the given LinkItem dict from the plugins host, to the given path. Proceeded with multiple connections
        :attr:`~unidown.plugin.a_plugin.APlugin._simul_downloads`. After
        :func:`~unidown.plugin.a_plugin.APlugin.check_download` is recommend.

        This function don't use an internal `link_item_dict`, `delay` or `folder` directly set in options or instance
        vars, because it can be used aside of the normal download routine inside the plugin itself for own things.
        As of this it still needs access to the logger, so a staticmethod is not possible.

        :param link_items: data which gets downloaded
        :param folder: target download folder
        :param desc: description of the progressbar
        :param unit: unit of the download, shown in the progressbar
        """
        # TODO: add other optional host?
        if len(link_items) == 0:
            return

        job_list = []
        with ThreadPoolExecutor(max_workers=self._simul_downloads) as executor:
            for link, item in link_items.items():
                job = executor.submit(self.download_as_file, link, folder.joinpath(item.name), self._options['delay'])
                job_list.append(job)

            pbar = tqdm(as_completed(job_list), total=len(job_list), desc=desc, unit=unit, mininterval=1, ncols=100, disable=self._disable_tqdm)
            for _ in pbar:
                pass

        for job in job_list:
            try:
                job.result()
            except HTTPError as ex:
                self.log.warning(f"Failed to download: {str(ex)}")

    def download_as_file(self, url: str, target_file: Path, delay: float = 0) -> str:
        """
        Download the given url to the given target folder.

        :param url: link
        :param target_file: target file
        :param delay: after download wait this much seconds
        :return: url
        :raises ~urllib3.exceptions.HTTPError: if the connection has an error
        """
        if target_file.exists():
            new_name = target_file
            while new_name.exists():
                new_name = new_name.with_name(f"{new_name.stem}_r{''.join(new_name.suffixes)}")
            target_file.rename(new_name)
            self.log.critical(f"target file exists! renaming '{target_file}' to '{new_name}'")

        with self._downloader.request('GET', url, preload_content=False, retries=urllib3.util.retry.Retry(3)) as reader:
            if reader.status == 200:
                with target_file.open(mode='wb') as writer:
                    writer.write(reader.data)
            else:
                raise HTTPError(f"{url} | {reader.status}")

        if delay > 0:
            time.sleep(delay)

        return url

    def check_download(self, link_item_dict: LinkItemDict, folder: Path, log: bool = False) -> Tuple[LinkItemDict, LinkItemDict]:
        """
        Check if the download of the given dict was successful. No proving if the content of the file is correct too.

        :param link_item_dict: dict which to check
        :param folder: folder where the downloads are saved
        :param log: if the lost items should be logged
        :return: succeeded and failed
        """
        succeed = LinkItemDict({link: item for link, item in link_item_dict.items() if folder.joinpath(item.name).is_file()})
        failed = LinkItemDict({link: item for link, item in link_item_dict.items() if link not in succeed})

        if failed and log:
            for link, item in failed.items():
                self.log.warning(f"Not downloaded: {self.info.host + link} - {item.name}")

        return succeed, failed

    def update_savestate(self, new_items: LinkItemDict):
        """
        Update savestate.

        :param new_items: new items
        """
        self._savestate.plugin_info = self.info
        self._savestate.last_update = self.last_update
        self._savestate.link_items.actualize(new_items)

    def save_savestate(self):
        """
        Save meta data about the downloaded things and the plugin to file.
        """
        with self._savestate_file.open(mode='w', encoding="utf8") as writer:
            writer.write(json.dumps(self._savestate.to_json()))

    def clean_up(self):
        """
        Default clean up for a module.
        Deletes :attr:`~unidown.plugin.a_plugin.APlugin._temp_dir`.
        """
        self._downloader.close()
        tools.unlink_dir_rec(self._temp_dir)

    def _load_default_options(self):
        """
        Loads default options if they were not passed at creation.
        """
        if 'delay' in self._options:
            try:
                self._options['delay'] = float(self._options['delay'])
            except ValueError:
                self._options['delay'] = 0
                self.log.warning(f"Plugin option 'delay' was not a float. Using {self._options['delay']}s.")
        else:
            self._options['delay'] = 0
            self.log.warning(f"Plugin option 'delay' is missing. Using {self._options['delay']}s.")

    @staticmethod
    def get_plugins() -> Dict[str, pkg_resources.EntryPoint]:
        """
        Get all available plugins for unidown.

        :return: plugin name list
        """
        return {entry.name: entry for entry in pkg_resources.iter_entry_points('unidown.plugin')}
