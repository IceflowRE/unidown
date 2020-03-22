import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import certifi
import pkg_resources
import urllib3
import urllib3.util
from packaging.version import Version
from tqdm import tqdm
from urllib3.exceptions import HTTPError

from unidown import dynamic_data, tools
from unidown.plugin.exceptions import PluginException
from unidown.plugin.link_item_dict import LinkItemDict
from unidown.plugin.plugin_info import PluginInfo
from unidown.plugin.savestate import SaveState


class APlugin(ABC):
    """
    Abstract class of a plugin. Provides all needed variables and methods.

    :param options: parameters which can included optional parameters
    :raises ~unidown.plugin.exceptions.PluginException: can not create default plugin paths

    :ivar _log: use this for logging **| do not edit**
    :ivar _simul_downloads: number of simultaneous downloads
    :ivar _info: information about the plugin **| do not edit**
    :ivar _temp_path: path where the plugin can place all temporary data **| do not edit**
    :ivar _download_path: general download path of the plugin **| do not edit**
    :ivar _savestate_file: file which contains the latest savestate of the plugin **| do not edit**
    :ivar _last_update: latest update time of the referencing data **| do not edit**
    :ivar _unit: the thing which should be downloaded, may be displayed in the progress bar
    :ivar _download_data: referencing data **| do not edit**
    :ivar _downloader: downloader which will download the data **| do not edit**
    :ivar _options: options which the plugin uses internal, should be used for the given options at init
    """
    _info: PluginInfo = None

    def __init__(self, options: List[str] = None):
        if self._info is None:
            raise ValueError("info is not set.")

        self._log: logging.Logger = logging.getLogger(self._info.name)
        self._simul_downloads: int = dynamic_data.USING_CORES

        self._temp_path: Path = dynamic_data.TEMP_DIR.joinpath(self.name)
        self._download_path: Path = dynamic_data.DOWNLOAD_DIR.joinpath(self.name)
        self._savestate_file: Path = dynamic_data.SAVESTATE_DIR.joinpath(self.name + '_save.json')

        try:
            self._temp_path.mkdir(parents=True, exist_ok=True)
            self._download_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise PluginException('Can not create default plugin paths, due to a permission error.')

        self._last_update: datetime = datetime(1970, 1, 1)
        self._unit: str = 'item'
        self._download_data: LinkItemDict = LinkItemDict()
        self._downloader: urllib3.HTTPSConnectionPool = urllib3.HTTPSConnectionPool(
            self.info.host, maxsize=self._simul_downloads, cert_reqs='CERT_REQUIRED', ca_certs=certifi.where()
        )

        self._savestate: SaveState = SaveState(dynamic_data.SAVESTATE_VERSION, self.info, self.last_update,
                                               LinkItemDict())

        # load options
        self._options: Dict[str, Any] = self._get_options_dict(options)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.info == other.info

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    @property
    def log(self) -> logging.Logger:
        return self._log

    @property
    def simul_downloads(self) -> int:
        return self._simul_downloads

    @property
    def info(self) -> PluginInfo:
        return self._info

    @property
    def host(self) -> str:
        return self._info.host

    @property
    def name(self) -> str:
        return self._info.name

    @property
    def version(self) -> Version:
        return self._info.version

    @property
    def temp_path(self) -> Path:
        return self._temp_path

    @property
    def download_path(self) -> Path:
        return self._download_path

    @property
    def savestate(self):
        return self._savestate

    @property
    def last_update(self) -> datetime:
        return self._last_update

    @property
    def download_data(self) -> LinkItemDict:
        return self._download_data

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def options(self) -> Dict[str, Any]:
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

        with self._savestate_file.open(mode='r', encoding="utf8") as data_file:
            try:
                savestate_json = json.loads(data_file.read())
            except Exception:
                raise PluginException(
                    f"Broken savestate json. Please fix or delete this file (you may lose data in this case): {self._savestate_file}")

        try:
            savestate = SaveState.from_json(savestate_json)
        except Exception as ex:
            raise PluginException(f"Could not load savestate from json {self._savestate_file}: {ex}")
        else:
            del savestate_json

        if savestate.version != dynamic_data.SAVESTATE_VERSION:
            raise PluginException("Different save state version handling is not implemented yet.")

        if savestate.plugin_info.version != self.info.version:
            raise PluginException("Different plugin version handling is not implemented yet.")

        if savestate.plugin_info.name != self.info.name:
            raise PluginException("Save state plugin ({name}) does not match the current ({cur_name}).".format(
                name=savestate.plugin_info.name, cur_name=self.name))
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
    def _create_download_links(self) -> LinkItemDict:
        """
        Get the download links in a specific format.
        **Has to be implemented inside Plugins.**

        :raises NotImplementedError: abstract method
        """
        raise NotImplementedError

    def update_download_links(self):
        """
        Update the download links. Calls :func:`~unidown.plugin.a_plugin.APlugin._create_download_links`.
        """
        self._download_data = self._create_download_links()

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
        :param delay: delay between the downloads in seconds
        """
        # TODO: add other optional host?
        if not link_items:
            return

        job_list = []
        with ThreadPoolExecutor(max_workers=self._simul_downloads) as executor:
            for link, item in link_items.items():
                job = executor.submit(self.download_as_file, link, folder, item.name, self._options['delay'])
                job_list.append(job)

            pbar = tqdm(as_completed(job_list), total=len(job_list), desc=desc, unit=unit, leave=True, mininterval=1,
                        ncols=100, disable=dynamic_data.DISABLE_TQDM)
            for _ in pbar:
                pass

        for job in job_list:
            try:
                job.result()
            except HTTPError as ex:
                self.log.warning("Failed to download: " + str(ex))
                # Todo: connection lost handling (check if the connection to the server itself is lost)

    def download_as_file(self, url: str, folder: Path, name: str, delay: float = 0) -> str:
        """
        Download the given url to the given target folder.

        :param url: link
        :param folder: target folder
        :param name: target file name
        :param delay: after download wait in seconds
        :return: url
        :raises ~urllib3.exceptions.HTTPError: if the connection has an error
        """
        while folder.joinpath(name).exists():  # TODO: handle already existing files
            self.log.warning('already exists: ' + name)
            name = name + '_d'

        with self._downloader.request('GET', url, preload_content=False, retries=urllib3.util.retry.Retry(3)) as reader:
            if reader.status == 200:
                with folder.joinpath(name).open(mode='wb') as out_file:
                    out_file.write(reader.data)
            else:
                raise HTTPError(f"{url} | {reader.status}")

        if delay > 0:
            time.sleep(delay)

        return url

    def check_download(self, link_item_dict: LinkItemDict, folder: Path, log: bool = True) -> Tuple[
        LinkItemDict, LinkItemDict]:
        """
        Check if the download of the given dict was successful. No proving if the content of the file is correct too.

        :param link_item_dict: dict which to check
        :param folder: folder where the downloads are saved
        :param log: if the lost items should be logged
        :return: succeeded and failed
        """
        succeed = LinkItemDict(
            {link: item for link, item in link_item_dict.items() if folder.joinpath(item.name).is_file()})
        failed = LinkItemDict({link: item for link, item in link_item_dict.items() if link not in succeed})

        if failed and log:
            for link, item in failed.items():
                self.log.error(f"Not downloaded: {self.info.host + link} - {item.name}")

        return succeed, failed

    def update_savestate(self, new_items: LinkItemDict):
        """
        Update savestate.

        :param new_items: new items
        """
        self._savestate.link_items.actualize(new_items)
        self._savestate = SaveState(dynamic_data.SAVESTATE_VERSION, self.info, self.last_update,
                                    self._savestate.link_items)

    def save_savestate(self):  # TODO: add progressbar
        """
        Save meta data about the downloaded things and the plugin to file.

        :param data_dict: data
        """
        with self._savestate_file.open(mode='w', encoding="utf8") as writer:
            writer.write(json.dumps(self._savestate.to_json()))

    def clean_up(self):
        """
        Default clean up for a module.
        Deletes :attr:`~unidown.plugin.a_plugin.APlugin._temp_path`.
        """
        self._downloader.close()
        tools.unlink_dir_rec(self._temp_path)

    def delete_data(self):
        """
        Delete everything which is related to the plugin. **Do not use if you do not know what you do!**
        """
        self.clean_up()
        tools.unlink_dir_rec(self._download_path)
        if self._savestate_file.exists():
            self._savestate_file.unlink()

    def _get_options_dict(self, options: List[str]) -> Dict[str, Any]:
        """
        Convert the option list to a dictionary where the key is the option and the value is the related option.
        Is called in the init.

        :param options: options given to the plugin.
        :return: dictionary which contains the option key as str related to the option string
        """
        if options is None:
            options = []
        plugin_options = {}
        for option in options:
            cur_option = option.split("=")
            if len(cur_option) != 2:
                self.log.warning(f"'{option}' is not valid and will be ignored.")
                continue
            plugin_options[cur_option[0]] = cur_option[1]

        if "delay" in plugin_options:
            try:
                plugin_options['delay'] = float(plugin_options['delay'])
            except ValueError:
                plugin_options['delay'] = 0
                self.log.warning("Plugin option 'delay' is not a float. Using default.")
        else:
            plugin_options['delay'] = 0
            self.log.warning("Plugin option 'delay' is missing. Using default.")
        return plugin_options

    @staticmethod
    def get_plugins() -> Dict[str, pkg_resources.EntryPoint]:
        """
        Get all available plugins for unidown.

        :return: plugin name list
        """
        return {entry.name: entry for entry in pkg_resources.iter_entry_points('unidown.plugin')}
