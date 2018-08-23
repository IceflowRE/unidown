import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import certifi
import pkg_resources
import urllib3
import urllib3.util
from google.protobuf import json_format
from google.protobuf.json_format import ParseError
from packaging.version import Version
from tqdm import tqdm
from urllib3.exceptions import HTTPError

from unidown import dynamic_data
from unidown.plugin.exceptions import PluginException
from unidown.plugin.link_item import LinkItem
from unidown.plugin.plugin_info import PluginInfo
from unidown.plugin.protobuf.save_state_pb2 import SaveStateProto
from unidown.plugin.save_state import SaveState
from unidown.tools import create_dir_rec, delete_dir_rec


class APlugin(ABC):
    """
    Abstract class of a plugin. Provides all needed variables and methods.

    :param info: information about the plugin
    :type info: ~unidown.plugin.plugin_info.PluginInfo
    :param options: parameters which can included optional parameters
    :type options: List[str]
    :raises ~unidown.plugin.exceptions.PluginException: can not create default plugin paths

    :ivar _log: use this for logging **| do not edit**
    :vartype _log: ~logging.Logger
    :ivar _simul_downloads: number of simultaneous downloads
    :vartype _simul_downloads: int
    :ivar _info: information about the plugin **| do not edit**
    :vartype _info: ~unidown.plugin.plugin_info.PluginInfo
    :ivar _temp_path: path where the plugin can place all temporary data **| do not edit**
    :vartype _temp_path: ~pathlib.Path
    :ivar _download_path: general download path of the plugin **| do not edit**
    :vartype _download_path: ~pathlib.Path
    :ivar _save_state_file: file which contains the latest savestate of the plugin **| do not edit**
    :vartype _save_state_file: ~pathlib.Path
    :ivar _last_update: latest update time of the referencing data **| do not edit**
    :vartype _last_update: ~datetime.datetime
    :ivar _unit: the thing which should be downloaded, may be displayed in the progress bar
    :vartype _unit: str
    :ivar _download_data: referencing data **| do not edit**
    :vartype _download_data: Dict[str, ~unidown.plugin.link_item.LinkItem]
    :ivar _downloader: downloader which will download the data **| do not edit**
    :vartype _downloader: ~urllib3.HTTPSConnectionPool
    :ivar _options: options which the plugin uses internal, should be used for the given options at init
    :vartype _options: Dict[str, ~typing.Any]
    """

    def __init__(self, info: PluginInfo, options: List[str] = None):
        if options is None:
            options = []

        self._log = logging.getLogger(info.name)
        self._simul_downloads = dynamic_data.USING_CORES

        self._info = info  # info about the module
        self._temp_path = dynamic_data.TEMP_DIR.joinpath(self.name)  # module temp path
        self._download_path = dynamic_data.DOWNLOAD_DIR.joinpath(self.name)  # module download path
        self._save_state_file = dynamic_data.SAVESTAT_DIR.joinpath(self.name + '_save.json')  # module save path

        try:
            create_dir_rec(self._temp_path)
            create_dir_rec(self._download_path)
        except PermissionError:
            raise PluginException('Can not create default plugin paths, due to a permission error.')

        self._last_update = datetime(1970, 1, 1)
        self._unit = 'item'
        self._download_data = {}
        self._downloader = urllib3.HTTPSConnectionPool(self.info.host, maxsize=self._simul_downloads,
                                                       cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

        # load options
        # supported: delay
        self._options = {}
        for option in options:
            if option.startswith('delay='):
                try:
                    self._options['delay'] = float(option[6:])
                except ValueError:
                    # TODO: bypasses log.disabled
                    self.log.warning("Plugin option 'delay' is not a float. Using default.")

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
    def download_path(self) -> Path:
        return self._download_path

    @property
    def last_update(self) -> datetime:
        return self._last_update

    @property
    def download_data(self) -> Dict[str, LinkItem]:
        return self._download_data

    @property
    def unit(self) -> str:
        return self._unit

    @abstractmethod
    def _create_download_links(self) -> Dict[str, LinkItem]:
        """
        Get the download links in a specific format.
        **Has to be implemented inside Plugins.**

        :rtype: Dict[str, ~unidown.plugin.link_item.LinkItem]
        :raises NotImplementedError: abstract method
        """
        raise NotImplementedError

    @abstractmethod
    def _create_last_update_time(self) -> datetime:
        """
        Get the newest update time from the referencing data.
        **Has to be implemented inside Plugins.**

        :rtype: ~datetime.datetime
        :raises NotImplementedError: abstract method
        """
        raise NotImplementedError

    def update_last_update(self):
        """
        Call this to update the latest update time. Calls :func:`~unidown.plugin.a_plugin.APlugin._create_last_update_time`.
        """
        self._last_update = self._create_last_update_time()

    def update_download_links(self):
        """
        Update the download links. Calls :func:`~unidown.plugin.a_plugin.APlugin._create_download_links`.
        """
        self._download_data = self._create_download_links()

    # TODO: parallelize?
    def check_download(self, link_item_dict: Dict[str, LinkItem], folder: Path, log: bool = True) -> Tuple[
        Dict[str, LinkItem], Dict[str, LinkItem]]:
        """
        Check if the download of the given dict was successful. No proving if the content of the file is correct too.

        :param link_item_dict: dict which to check
        :type link_item_dict: Dict[str, ~unidown.plugin.link_item.LinkItem]
        :param folder: folder where the downloads are saved
        :type folder: ~pathlib.Path
        :param log: if the lost items should be logged
        :type log: bool
        :return: succeeded and lost dicts
        :rtype: Tuple[Dict[str, ~unidown.plugin.link_item.LinkItem], Dict[str, ~unidown.plugin.link_item.LinkItem]]
        """
        succeed = {link: item for link, item in link_item_dict.items() if folder.joinpath(item.name).is_file()}
        lost = {link: item for link, item in link_item_dict.items() if link not in succeed}

        if lost and log:
            for link, item in lost.items():
                self.log.error(f"Not downloaded: {self.info.host+link} - {item.name}")

        return succeed, lost

    def clean_up(self):
        """
        Default clean up for a module.
        Deletes :attr:`~unidown.plugin.a_plugin.APlugin._temp_path`.
        """
        self._downloader.close()
        delete_dir_rec(self._temp_path)

    def delete_data(self):
        """
        Delete everything which is related to the plugin. **Do not use if you do not know what you do!**
        """
        self.clean_up()
        delete_dir_rec(self._download_path)
        if self._save_state_file.exists():
            self._save_state_file.unlink()

    def download_as_file(self, url: str, folder: Path, name: str, delay: float = 0) -> str:
        """
        Download the given url to the given target folder.

        :param url: link
        :type url: str
        :param folder: target folder
        :type folder: ~pathlib.Path
        :param name: target file name
        :type name: str
        :param delay: after download wait in seconds
        :type delay: float
        :return: url
        :rtype: str
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

    def download(self, link_item_dict: Dict[str, LinkItem], folder: Path, desc: str, unit: str, delay: float = 0) -> \
            List[str]:
        """
        Download the given LinkItem dict from the plugins host, to the given path. Proceeded with multiple connections
        :attr:`~unidown.plugin.a_plugin.APlugin._simul_downloads`. After
        :func:`~unidown.plugin.a_plugin.APlugin.check_download` is recommend.

        :param link_item_dict: data which gets downloaded
        :type link_item_dict: Dict[str, ~unidown.plugin.link_item.LinkItem]
        :param folder: target download folder
        :type folder: ~pathlib.Path
        :param desc: description of the progressbar
        :type desc: str
        :param unit: unit of the download, shown in the progressbar
        :type unit: str
        :param delay: delay between the downloads in seconds
        :type delay: float
        :return: list of urls of downloads without errors
        :rtype: List[str]
        """
        if 'delay' in self._options:
            delay = self._options['delay']
        # TODO: add other optional host?
        if not link_item_dict:
            return []

        job_list = []
        with ThreadPoolExecutor(max_workers=self._simul_downloads) as executor:
            for link, item in link_item_dict.items():
                job = executor.submit(self.download_as_file, link, folder, item.name, delay)
                job_list.append(job)

            pbar = tqdm(as_completed(job_list), total=len(job_list), desc=desc, unit=unit, leave=True, mininterval=1,
                        ncols=100, disable=dynamic_data.DISABLE_TQDM)
            for _ in pbar:
                pass

        download_without_errors = []
        for job in job_list:
            try:
                download_without_errors.append(job.result())
            except HTTPError as ex:
                self.log.warning("Failed to download: " + str(ex))
                # Todo: connection lost handling (check if the connection to the server itself is lost)

        return download_without_errors

    def _create_save_state(self, link_item_dict: Dict[str, LinkItem]) -> SaveState:
        """
        Create protobuf savestate of the module and the given data.

        :param link_item_dict: data
        :type link_item_dict: Dict[str, ~unidown.plugin.link_item.LinkItem]
        :return: the savestate
        :rtype: ~unidown.plugin.save_state.SaveState
        """
        return SaveState(dynamic_data.SAVE_STATE_VERSION, self.info, self.last_update, link_item_dict)

    def save_save_state(self, data_dict: Dict[str, LinkItem]):  # TODO: add progressbar
        """
        Save meta data about the downloaded things and the plugin to file.

        :param data_dict: data
        :type data_dict: Dict[link, ~unidown.plugin.link_item.LinkItem]
        """
        json_data = json_format.MessageToJson(self._create_save_state(data_dict).to_protobuf())
        with self._save_state_file.open(mode='w', encoding="utf8") as writer:
            writer.write(json_data)

    def load_save_state(self) -> SaveState:
        """
        Load the savestate of the plugin.

        :return: savestate
        :rtype: ~unidown.plugin.save_state.SaveState
        :raises ~unidown.plugin.exceptions.PluginException: broken savestate json
        :raises ~unidown.plugin.exceptions.PluginException: different savestate versions
        :raises ~unidown.plugin.exceptions.PluginException: different plugin versions
        :raises ~unidown.plugin.exceptions.PluginException: different plugin names
        :raises ~unidown.plugin.exceptions.PluginException: could not parse the protobuf
        """
        if not self._save_state_file.exists():
            self.log.info("No savestate file found.")
            return SaveState(dynamic_data.SAVE_STATE_VERSION, self.info, datetime(1970, 1, 1), {})

        savestat_proto = ""
        with self._save_state_file.open(mode='r', encoding="utf8") as data_file:
            try:
                savestat_proto = json_format.Parse(data_file.read(), SaveStateProto(), ignore_unknown_fields=False)
            except ParseError:
                raise PluginException(
                    f"Broken savestate json. Please fix or delete (you may lose data in this case) the file: {self._save_state_file}")

        try:
            save_state = SaveState.from_protobuf(savestat_proto)
        except ValueError as ex:
            raise PluginException(f"Could not parse the protobuf {self._save_state_file}: {ex}")
        else:
            del savestat_proto

        if save_state.version != dynamic_data.SAVE_STATE_VERSION:
            raise PluginException("Different save state version handling is not implemented yet.")

        if save_state.plugin_info.version != self.info.version:
            raise PluginException("Different plugin version handling is not implemented yet.")

        if save_state.plugin_info.name != self.name:
            raise PluginException("Save state plugin ({name}) does not match the current ({cur_name}).".format(
                name=save_state.plugin_info.name, cur_name=self.name))
        return save_state

    def get_updated_data(self, old_data: Dict[str, LinkItem]) -> Dict[str, LinkItem]:
        """
        Get links who needs to be downloaded by comparing old and the new data.

        :param old_data: old data
        :type old_data: Dict[str, ~unidown.plugin.link_item.LinkItem]
        :return: data which is newer or dont exist in the old one
        :rtype: Dict[str, ~unidown.plugin.link_item.LinkItem]
        """
        if not self.download_data:
            return {}
        new_link_item_dict = {}
        for link, link_item in tqdm(self.download_data.items(), desc="Compare with save", unit="item", leave=True,
                                    mininterval=1, ncols=100, disable=dynamic_data.DISABLE_TQDM):
            # TODO: add methode to log lost items, which are in old but not in new
            if link in new_link_item_dict:  # TODO: is ever false, since its the key of a dict: move to the right place
                self.log.warning("Duplicate: " + link + " - " + new_link_item_dict[link] + " : " + link_item)

            # if the new_data link does not exists in old_data or new_data time is newer
            if (link not in old_data) or (link_item.time > old_data[link].time):
                new_link_item_dict[link] = link_item

        return new_link_item_dict

    def update_dict(self, base: Dict[str, LinkItem], new: Dict[str, LinkItem]):
        """
        Use for updating save state dicts and get the new save state dict. Provides a debug option at info level.
        Updates the base dict. Basically executes `base.update(new)`.

        :param base: base dict **gets overridden!**
        :type base: Dict[str, ~unidown.plugin.link_item.LinkItem]
        :param new: data which updates the base
        :type new: Dict[str, ~unidown.plugin.link_item.LinkItem]
        """
        if logging.INFO >= logging.getLevelName(dynamic_data.LOG_LEVEL):  # TODO: logging here or outside
            for link, item in new.items():
                if link in base:
                    self.log.info('Actualize item: ' + link + ' | ' + str(base[link]) + ' -> ' + str(item))
        base.update(new)

    @staticmethod
    def get_plugins() -> Dict[str, pkg_resources.EntryPoint]:
        """
        Get all available plugins for unidown.

        :return: plugin name list
        :rtype: Dict[str, ~pkg_resources.EntryPoint]
        """
        return {entry.name: entry for entry in pkg_resources.iter_entry_points('unidown.plugin')}
