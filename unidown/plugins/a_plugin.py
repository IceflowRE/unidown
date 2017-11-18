import logging
import pkgutil
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import certifi
import urllib3
import urllib3.util
from google.protobuf import json_format
from tqdm import tqdm
from urllib3.exceptions import HTTPError

import unidown.core.data.dynamic as dynamic_data
from unidown.plugins.data.plugin_info import PluginInfo
from unidown.plugins.data.protobuf.save_state_pb2 import SaveStateProto
from unidown.plugins.data.save_state import SaveState
from unidown.plugins.exceptions import PluginException
from unidown.tools.tdqm_option import TdqmOption
from unidown.tools.tools import create_dir_rec, delete_dir_rec, progress_bar


class APlugin(ABC):
    """
    Abstract class of a module. Provides all needed variables and methodes.

    :param info: informations about the plugin
    :type info: ~unidown.plugins.data.plugin_info.PluginInfo
    :raises PermissionError: can not create default plugin paths

    :ivar _info: informations about the plugin, access with :func:`~unidown.plugins.a_plugin.APlugin.info`
                 **| do not edit**
    :vartype _info: ~unidown.plugins.data.plugin_info.PluginInfo
    :ivar log: use this for logging **| do not edit**
    :vartype log: ~logging.Logger
    :ivar temp_path: path where the plugin can place all temporary data **| do not edit**
    :vartype temp_path: ~pathlib.Path
    :ivar simul_downloads: number of simultaneous downloads
    :vartype simul_downloads: int
    :ivar unit: the thing which should be downloaded
    :vartype unit: str
    :ivar _download_path: general download path of the plugin **| do not edit**
    :vartype _download_path: ~pathlib.Path
    :ivar save_state_file: file which contains the latest savestate of the plugin **| do not edit**
    :vartype save_state_file: ~pathlib.Path
    :ivar downloader: downloader which will download the data **| do not edit**
    :vartype downloader: ~urllib3.HTTPSConnectionPool
    :ivar _last_update: latest update time of the referencing data, access with
                        :func:`~unidown.plugins.a_plugin.APlugin.last_update` **| do not edit**
    :vartype _last_update: ~datetime.datetime
    """

    def __init__(self, info: PluginInfo):
        self.log = logging.getLogger(info.name)
        self.simul_downloads = dynamic_data.USING_CORES

        self._info = info  # info about the module
        self.temp_path = dynamic_data.TEMP_DIR.joinpath(self.name)  # module temp path
        self._download_path = dynamic_data.DOWNLOAD_DIR.joinpath(self.name)  # module download path
        self.save_state_file = dynamic_data.SAVESTAT_DIR.joinpath(self.name + '_save.json')  # module save path

        try:
            create_dir_rec(self.temp_path)
            create_dir_rec(self._download_path)
        except PermissionError:
            raise PluginException('Can not create default plugin paths, due to a permission error.')

        self._last_update = datetime(1970, 1, 1)
        self.unit = 'item'
        self.downloader = urllib3.HTTPSConnectionPool(self.info.host, maxsize=self.simul_downloads,
                                                      cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.info == other.info

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def info(self):
        """

        :rtype: ~unidown.plugins.data.plugin_info.PluginInfo
        """
        return self._info

    @property
    def host(self):
        """

        :rtype: str
        """
        return self._info.host

    @property
    def name(self):
        """

        :rtype: str
        """
        return self._info.name

    @property
    def version(self):
        """

        :rtype: ~packaging.version.Version
        """
        return self._info.version

    @property
    def last_update(self):
        """

        :rtype: ~datetime.datetime
        """
        return self._last_update

    @abstractmethod
    def _create_download_links(self):  # TODO: -> typing.Dict[str, LinkItem]: get it work
        """
        Get the download links in a specific format.
        **Has to be implemented inside Plugins.**

        :rtype: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        """
        raise NotImplementedError

    @abstractmethod
    def _create_last_update(self) -> datetime:
        """
        Get the last update of the data.
        **Has to be implemented inside Plugins.**

        :rtype: ~datetime.datetime
        """
        raise NotImplementedError

    def get_download_links(self):
        """

        :rtype: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        """
        return self._create_download_links()

    def update_last_update(self):
        """
        Call this to update the latest update time.

        :rtype: ~datetime.datetime
        """
        self._last_update = self._create_last_update()
        return self._last_update

    def check_download(self, link_item_dict: dict, folder: Path, log=True):  # TODO: parallelize?
        """
        Checks if the download of the given dict was successful. No proving if the content of the file is correct too.

        :param link_item_dict: dict which to check
        :type link_item_dict: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        :param folder: folder where the download had to be downloaded
        :type folder: ~pathlib.Path
        :param log: if lost items should be logged
        :type log: bool
        :return: succeeded and lost dicts as dict(link, ~unidown.plugins.data.link_item.LinkItem)
        :rtype: dict(str, ~unidown.plugins.data.link_item.LinkItem), dict(str, ~unidown.plugins.data.link_item.LinkItem)
        """
        succeed = {link: item for link, item in link_item_dict.items() if folder.joinpath(item.name).is_file()}
        lost = {link: item for link, item in link_item_dict.items() if link not in succeed}

        if lost and log:
            for link, item in lost.items():
                self.log.error('Not downloaded: {url} - {name}'.format(url=self.info.host + link, name=item.name))

        return succeed, lost

    def clean_up(self):
        """
        Default clean up for a module.
        Deletes :attr:`~unidown.plugins.a_plugin.APlugin.temp_path`
        """
        if self.downloader.pool is not None:  # TODO: as long as urllib3 #1279 is open
            self.downloader.close()
        delete_dir_rec(self.temp_path)

    def delete_data(self):
        """
        Deletes everything which is related to the plugin. **Do not use if you do not know what you do!**
        """
        self.clean_up()
        delete_dir_rec(self._download_path)
        if self.save_state_file.exists():
            self.save_state_file.unlink()

    def download_as_file(self, url, folder: Path, name: str):
        """
        Download the given url to the given target folder.

        :param url: link
        :type url: str
        :param folder: target folder
        :type folder: ~pathlib.Path
        :param name: target file name
        :type name: str
        :return: url
        :rtype: str
        :raises ~urllib3.exceptions.HTTPError: if the connection has an error
        """
        while folder.joinpath(name).exists():  # TODO: handle already existing files
            self.log.warning('already exists: ' + name)
            name = name + '_d'

        with self.downloader.request('GET', url, preload_content=False, retries=urllib3.util.retry.Retry(3)) as reader:
            if reader.status == 200:
                with folder.joinpath(name).open(mode='wb') as out_file:
                    out_file.write(reader.data)
            else:
                raise HTTPError("{url} | {status}".format(url=url, status=str(reader.status)))

        return url

    def download(self, link_item_dict: dict, folder: Path, progress_bar_option: TdqmOption):
        """
        Download the given LinkItem dict from the modules host, to the given path. Proceeded with multiple connections.
        After check_download is recommend.

        :type link_item_dict: dict(link, ~unidown.plugins.data.link_item.LinkItem)
        :param folder: target download folder
        :type folder: ~pathlib.Path
        :param progress_bar_option: progress bar of the download
        :type progress_bar_option: ~unidown.tools.tqdm_options.TqdmOption
        :return: list of urls of downloads without errors
        :rtype: list[str]
        """
        # TODO: add other optional host?
        if not link_item_dict:
            return []

        job_list = []
        with ThreadPoolExecutor(max_workers=self.simul_downloads) as executor:
            for link, item in link_item_dict.items():
                job = executor.submit(self.download_as_file, link, folder, item.name)
                job_list.append(job)

            progress_bar(job_list, progress_bar_option)  # TODO: rework progress bars in plugin, add to others? remove?

        download_without_errors = []
        for job in job_list:
            try:
                download_without_errors.append(job.result())
            except HTTPError as ex:
                self.log.warning("Failed to download: " + str(ex))
                # Todo: connection lost handling (check if the connection to the server itself is lost)

        return download_without_errors

    def _create_save_state(self, link_item_dict: dict):
        """
        Create protobuf savestate of the module and the given data.

        :param link_item_dict: data
        :type link_item_dict: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        :return: protobuf
        :rtype: ~unidown.plugins.data.save_state.SaveState
        """
        return SaveState(dynamic_data.SAVE_STATE_VERSION, self.last_update, self.info, link_item_dict)

    def save_save_state(self, data_dict):  # TODO: add progressbar
        """
        Saves meta data about the downloaded things to file.

        :type data_dict: dict(link, ~unidown.plugins.data.link_item.LinkItem)
        """
        json_data = json_format.MessageToJson(self._create_save_state(data_dict).to_protobuf())
        with self.save_state_file.open(mode='w', encoding="utf8") as writer:
            writer.write(json_data)

    def load_save_state(self):
        """
        Load the savestate of the module.

        :rtype: ~unidown.plugins.data.save_state.SaveState
        :raises ~unidown.plugins.exceptions.PluginException: different savestate versions
        :raises ~unidown.plugins.exceptions.PluginException: different plugin versions
        :raises ~unidown.plugins.exceptions.PluginException: different plugin names
        """
        if not self.save_state_file.exists():
            self.log.info("No savestate file found.")
            return SaveState(dynamic_data.SAVE_STATE_VERSION, datetime(1970, 1, 1), self.info, {})

        with self.save_state_file.open(mode='r', encoding="utf8") as data_file:
            savestat_proto = json_format.Parse(data_file.read(), SaveStateProto(), ignore_unknown_fields=False)
            save_state = SaveState.from_protobuf(savestat_proto)
            del savestat_proto

        if save_state.version != dynamic_data.SAVE_STATE_VERSION:
            raise PluginException("Different save state version handling is not implemented yet.")

        if save_state.plugin_info.version != self.info.version:
            raise PluginException("Different plugin version handling is not implemented yet.")

        if save_state.plugin_info.name != self.name:
            raise PluginException(
                "Save state plugin (" + save_state.plugin_info.name + ") does not match the current (" + self.name + ").")

        if save_state.last_update is None:
            self.log.warning("update_date was not found in save file and set to 1970.01.01")
            save_state.last_update = datetime(1970, 1, 1)
        return save_state

    def compare_old_with_new_data(self, old_data, new_data):
        """
        Get links who needs to be downloaded by comparing old and new data.

        :param old_data: Old data, mapped as link to LinkItem.
        :type old_data: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        :param new_data: New data.
        :type new_data: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        :return: dict(link, LinkItem)
        :rtype: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        """
        if not new_data:
            return {}
        new_link_item_dict = {}
        for link, link_item in tqdm(new_data.items(), desc="Compare with save", unit="item", leave=True, mininterval=1,
                                    ncols=100, disable=dynamic_data.DISABLE_TQDM):
            # TODO: add methode to log lost items, which are in old but not in new
            if link in new_link_item_dict:  # TODO: is ever false, since its the key of a dict: move to the right place
                self.log.warning("Duplicate: " + link + " - " + new_link_item_dict[link] + " : " + link_item)

            # if the new_data link does not exists in old_data or new_data time is newer
            if (link not in old_data) or (link_item.time > old_data[link].time):
                new_link_item_dict[link] = link_item

        return new_link_item_dict

    def update_dict(self, base: dict, new: dict):
        """
        Use for updating save state dicts and get the new save state dict. Provides a debug option at info level.
        Updates the base dict.

        :type base: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        :type new: dict(str, ~unidown.plugins.data.link_item.LinkItem)
        """
        if logging.INFO >= logging.getLevelName(dynamic_data.LOG_LEVEL):  # TODO: logging here or outside
            for link, item in new.items():
                if link in base:
                    self.log.info('Actualize item: ' + link + ' | ' + str(base[link]) + ' -> ' + str(item))
        base.update(new)


def get_plugins():
    """

    :rtype: list[str]
    """
    import unidown.plugins

    package = unidown.plugins
    return [modname for _, modname, ispkg in pkgutil.iter_modules(path=package.__path__, prefix=package.__name__ + '.')
            if ispkg and modname != 'unidown.plugins.data']
