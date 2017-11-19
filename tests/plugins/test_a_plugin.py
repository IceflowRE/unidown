from datetime import datetime

from unidown.plugins.a_plugin import APlugin
from unidown.plugins.data.link_item import LinkItem
from unidown.plugins.data.plugin_info import PluginInfo


class Plugin(APlugin):
    """
    Test plugin.
    """

    def __init__(self, info: PluginInfo = None):
        if info is None:
            super().__init__(PluginInfo('test', '1.0.0', 'raw.githubusercontent.com'))
        else:
            super().__init__(info)

    def _create_download_links(self):
        return {'/IceflowRE/MR-eBook-Downloader/master/README.md':
                    LinkItem('README.md', datetime(2000, 1, 1, hour=1, minute=1, second=1)),
                '/IceflowRE/MR-eBook-Downloader/master/no_file_here':
                    LinkItem('LICENSE', datetime(2002, 2, 2, hour=2, minute=2, second=2))
                }

    def _create_last_update_time(self):
        return datetime(1999, 9, 9, hour=9, minute=9, second=9)
