from datetime import datetime
from typing import List

from unidown.plugin import APlugin, LinkItem, PluginException, PluginInfo


class Plugin(APlugin):
    """
    Test plugin.
    """
    _info = PluginInfo('test', '1.0.0', 'raw.githubusercontent.com')

    def __init__(self, options: List[str] = None):
        super().__init__(options)
        self._options['behaviour'] = 'normal'
        if options is not None:
            for option in options:
                if option.startswith('behaviour='):
                    self._options['behaviour'] = option[10:]
        if self._options['behaviour'] == 'load_crash':
            raise Exception("crash")

    def _create_download_links(self):
        return {
            '/IceflowRE/unidown/master/README.rst':
                LinkItem('README.rst', datetime(2000, 1, 1, hour=1, minute=1, second=1)),
            '/IceflowRE/unidown/master/no_file_here':
                LinkItem('LICENSE', datetime(2002, 2, 2, hour=2, minute=2, second=2))
        }

    def _create_last_update_time(self):
        if self._options['behaviour'] == "run_fail":
            raise PluginException('failed')
        elif self._options['behaviour'] == "run_crash":
            raise Exception("crashed")

        return datetime(1999, 9, 9, hour=9, minute=9, second=9)
