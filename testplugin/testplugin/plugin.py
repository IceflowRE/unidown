from datetime import datetime
from typing import List

from unidown.plugin.a_plugin import APlugin
from unidown.plugin.exceptions import PluginException
from unidown.plugin.link_item import LinkItem
from unidown.plugin.plugin_info import PluginInfo


class Plugin(APlugin):
    """
    Test plugin.
    """

    # TODO: param options as first param is a must -> add to doc
    def __init__(self, options: List[str] = None, info: PluginInfo = None):
        if info is None:
            super().__init__(PluginInfo('test', '1.0.0', 'raw.githubusercontent.com'), options)
        else:
            super().__init__(info, options)
        self._options['behaviour'] = 'normal'
        if options is not None:
            for option in options:
                if option.startswith('behaviour='):
                    self._options['behaviour'] = option[10:]
        if self._options['behaviour'] == 'load_crash':
            raise Exception("crash")

    def _create_download_links(self):
        return {
            '/IceflowRE/Universal-Downloader/master/README.rst':
                LinkItem('README.rst', datetime(2000, 1, 1, hour=1, minute=1, second=1)),
            '/IceflowRE/Universal-Downloader/master/no_file_here':
                LinkItem('LICENSE', datetime(2002, 2, 2, hour=2, minute=2, second=2))
        }

    def _create_last_update_time(self):
        if self._options['behaviour'] == "run_fail":
            raise PluginException('failed')
        elif self._options['behaviour'] == "run_crash":
            raise Exception("crashed")

        return datetime(1999, 9, 9, hour=9, minute=9, second=9)
