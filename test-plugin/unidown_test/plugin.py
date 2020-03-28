import json
from datetime import datetime
from typing import Dict, Any

from unidown_test.savestate import MySaveState

from unidown.core.settings import Settings
from unidown.plugin import APlugin, LinkItem, PluginException, PluginInfo
from unidown.plugin.link_item_dict import LinkItemDict


class Plugin(APlugin):
    """
    Test plugin.
    """
    _info = PluginInfo('test', '0.1.0', 'raw.githubusercontent.com')
    _savestate_cls = MySaveState

    def __init__(self, settings: Settings, options: Dict[str, Any] = None):
        super().__init__(settings, options)
        self._username: str = self._options['username']
        if self._options['behaviour'] == 'load_crash':
            raise Exception("crash")

    def _create_download_links(self) -> LinkItemDict:
        self.download_as_file('/IceflowRE/unidown/master/tests/item_dict.json', self._temp_path, 'item_dict.json')
        with self._temp_path.joinpath('item_dict.json').open(encoding='utf8') as reader:
            data = json.loads(reader.read())
        result = LinkItemDict()
        for link, item in data.items():
            result[link] = LinkItem(item['name'], datetime.strptime(item['time'], LinkItem.time_format))
        return result

    def _create_last_update_time(self) -> datetime:
        if self._options['behaviour'] == "run_fail":
            raise PluginException('failed')
        elif self._options['behaviour'] == "run_crash":
            raise Exception("crashed")
        self.download_as_file('/IceflowRE/unidown/master/tests/last_update_time.txt', self._temp_path, 'last_update_time.txt')
        with self._temp_path.joinpath('last_update_time.txt').open(encoding='utf8') as reader:
            return datetime.strptime(reader.read(), LinkItem.time_format)

    def _load_default_options(self):
        super(Plugin, self)._load_default_options()
        if 'behaviour' not in self._options:
            self.log.warning("Plugin option 'behaviour' is missing. Using default.")
            self._options['behaviour'] = 'normal'
        if 'username' not in self._options:
            self._options['username'] = ''

    def load_savestate(self):
        super(Plugin, self).load_savestate()
        # do not override set username by options
        if self._username == '':
            self._username = self.savestate.username

    def update_savestate(self, new_items: LinkItemDict):
        super(Plugin, self).update_savestate(new_items)
        self._savestate.username = self._username
