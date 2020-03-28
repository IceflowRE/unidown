from datetime import datetime
from typing import List, Dict, Any

from unidown_test.savestate import MySaveState

from undiwon.core.settings import Settings
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
        return LinkItemDict({
            '/IceflowRE/unidown/master/README.rst':
                LinkItem('README.rst', datetime(2000, 1, 1, hour=1, minute=1, second=1)),
            '/IceflowRE/unidown/master/missing':
                LinkItem('LICENSE', datetime(2002, 2, 2, hour=2, minute=2, second=2))
        })

    def _create_last_update_time(self) -> datetime:
        if self._options['behaviour'] == "run_fail":
            raise PluginException('failed')
        elif self._options['behaviour'] == "run_crash":
            raise Exception("crashed")

        return datetime(1999, 9, 9, hour=9, minute=9, second=9)

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
