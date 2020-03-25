from datetime import datetime
from typing import List

from unidown.plugin import APlugin, LinkItem, PluginException, PluginInfo
from unidown.plugin.link_item_dict import LinkItemDict
from core.settings import Settings


class Plugin(APlugin):
    """
    Test plugin.
    """
    _info = PluginInfo('test', '0.1.0', 'raw.githubusercontent.com')

    def __init__(self, settings: Settings, options: List[str] = None):
        super().__init__(settings, options)
        if 'behaviour' not in self._options:
            self._options['behaviour'] = 'normal'
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
