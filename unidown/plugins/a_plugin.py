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
    """

    def __init__(self, info: PluginInfo):
        self.logging = logging.getLogger(info.name)
        self.simul_downloads = dynamic_data.USING_CORES

        self._info = info  # info about the module
        self.temp_path = dynamic_data.TEMP_DIR.joinpath(self.name)  # module temp path
        self.download_path = dynamic_data.DOWNLOAD_DIR.joinpath(self.name)  # module download path
        self.save_state_file = dynamic_data.SAVESTAT_DIR.joinpath(self.name + '_save.json')  # module save path

        try:
            create_dir_rec(self.temp_path)
            create_dir_rec(self.download_path)
        except PermissionError:
            raise PluginException()

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
        return self._info

    @property
    def host(self):
        return self._info.host

    @property
    def name(self):
        return self._info.name

    @property
    def version(self):
        return self._info.version

    @property
    def last_update(self):
        return self._last_update

    @abstractmethod
    def _create_download_links(self):  # TODO: -> typing.Dict[str, LinkItem]: get it work
        """
        Get the download links in a specific format.
        Has to be implemented inside Plugins.
        :return: links as dict[link, LinkItem].
        """
        raise NotImplementedError

    @abstractmethod
    def _create_last_update(self) -> datetime:
        """
        Get the last update of the data.
        Has to be implemented inside Plugins.
        :return: datetime
        """
        raise NotImplementedError

    def get_download_links(self):
        return self._create_download_links()

    def update_last_update(self):
        self._last_update = self._create_last_update()
        return self._last_update

    def check_download(self, link_item_dict: dict, folder: Path, log=True):  # TODO: parallelize?
        """
        Checks if the download of the given dict was successful. No proving if the content of the file is correct too.
        :param link_item_dict: dict which to check
        :param folder: folder where the download had to be downloaded
        :param log: if lost items should be logged
        :return: succeeded and lost dicts as dict(link, LinkItem)
        """
        succeed = {link: item for link, item in link_item_dict.items() if folder.joinpath(item.name).is_file()}
        lost = {link: item for link, item in link_item_dict.items() if link not in succeed}

        if lost and log:
            for link, item in lost.items():
                self.logging.error('Not downloaded: {url} - {name}'.format(url=self.info.host + link, name=item.name))

        return succeed, lost

    def clean_up(self):
        """
        Default clean up for a module.
        """
        if self.downloader.pool is not None:  # as long as urllib3 #1279 is open
            self.downloader.close()
        delete_dir_rec(self.temp_path)

    def delete_data(self):
        self.clean_up()
        delete_dir_rec(self.download_path)
        if self.save_state_file.exists():
            self.save_state_file.unlink()

    def download_as_file(self, url, folder: Path, name: str):
        """
        Download the given url to the given target folder.
        :param url: link
        :param folder: target folder
        :param name: target file name
        :return: url
        """
        while folder.joinpath(name).exists():  # TODO: handle already existing files
            self.logging.warning('already exists: ' + name)
            name = name + '_d'

        with self.downloader.request('GET', url, preload_content=False, retries=urllib3.util.retry.Retry(3)) as reader:
            if reader.status == 200:
                with folder.joinpath(name).open(mode='wb') as out_file:
                    out_file.write(reader.data)
            else:
                raise HTTPError(str(reader.status))

        return url

    def download(self, link_item_dict: dict, folder: Path, progress_bar_option: TdqmOption):
        """
        Download the given LinkItem dict from the modules host, to the given path. Proceeded with multiple connections.
        After check_download is recommend.
        :param link_item_dict: dict[link: LinkItem]
        :param folder: target download folder
        :param progress_bar_option: progress bar of the download
        :return: list of urls of downloads without errors
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
            except HTTPError:
                pass  # possible extension for logging or connection lost handling
            except Exception:
                pass  # possible extension for logging

        return download_without_errors

    def _create_save_state(self, link_linkitem: dict):
        """
        Create protobuf savestate of the module and the given data.
        :param link_linkitem: data
        :return: protobuf
        """
        return SaveState(str(dynamic_data.SAVE_STATE_VERSION), self.last_update, self.info, link_linkitem)

    def save_save_state(self, data_dict):  # TODO: add progressbar
        """
        Saves meta data about the downloaded things to file.
        :param data_dict: dict[link, LinkItem]
        """
        json_data = json_format.MessageToJson(self._create_save_state(data_dict).to_protobuf())
        with self.save_state_file.open(mode='w', encoding="utf8") as writer:
            writer.write(json_data)

    def load_save_state(self):  # TODO: raise for everything an exception
        """
        Load the savestate of the module.
        :return savestate
        """
        if not self.save_state_file.exists():
            return SaveState(str(dynamic_data.SAVE_STATE_VERSION), datetime(1970, 1, 1), self.info, {})

        with self.save_state_file.open(mode='r', encoding="utf8") as data_file:
            savestat_proto = json_format.Parse(data_file.read(), SaveStateProto(), ignore_unknown_fields=False)
            save_state = SaveState.from_protobuf(savestat_proto)
            del savestat_proto

        if save_state.version != dynamic_data.SAVE_STATE_VERSION:
            raise NotImplementedError("Different save state version handling is not implemented yet.")

        if save_state.plugin_info.version != self.info.version:
            raise NotImplementedError("Different plugin version handling is not implemented yet.")

        if save_state.plugin_info.name != self.name:
            raise PluginException(
                "Save state plugin (" + save_state.plugin_info.name + ") does not match the current (" + self.name + ").")

        if save_state.last_update is None:
            self.logging.warning("update_date was not found in save file and set to 1970.01.01")
            save_state.last_update = datetime(1970, 1, 1)
        return save_state

    def compare_old_with_new_data(self, old_data, new_data):
        """
        Get links who needs to be downloaded by comparing old and new data.
        :param old_data:
        :param new_data:
        :return: new dict[link, LinkItem]
        """
        if not new_data:
            return {}
        new_link_item_dict = {}
        for link, link_item in tqdm(new_data.items(), desc="Compare with save", unit="item", leave=True, mininterval=1,
                                    ncols=100, disable=dynamic_data.DISABLE_TQDM):
            # TODO: add methode to log lost items, which are in old but not in new
            if link in new_link_item_dict:  # TODO: is ever false, since its the key of a dict: move to the right place
                self.logging.warning("Duplicate: " + link + " - " + new_link_item_dict[link] + " : " + link_item)

            # if the new_data link does not exists in old_data or new_data time is newer
            if (link not in old_data) or (link_item.time > old_data[link].time):
                new_link_item_dict[link] = link_item

        return new_link_item_dict

    def update_dict(self, base: dict, new: dict):
        """
        Use for updating save state dicts and get the new save state dict. Provides a debug option at info level.
        :param base:
        :param new:
        """
        if logging.INFO >= logging.getLevelName(dynamic_data.LOG_LEVEL):  # TODO: logging here or outside
            for link, item in new.items():
                if link in base:
                    self.logging.info('Actualize item: ' + link + ' | ' + str(base[link]) + ' -> ' + str(item))
        base.update(new)


def get_plugins():
    import unidown.plugins

    package = unidown.plugins
    return [modname for _, modname, ispkg in pkgutil.iter_modules(path=package.__path__, prefix=package.__name__ + '.')
            if ispkg and modname != 'unidown.plugins.data']
