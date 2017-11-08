"""
Default exceptions of plugins.
"""


class PluginException(Exception):
    """
    Base class for exceptions in a plugin.
    If catching this, it implicit that the plugin is unable to work further.
    """

    def __init__(self, msg=''):
        self.msg = msg


class LastUpdateException(PluginException):
    """
    If the last update of the data from a plugin could not get correctly.
    """

    def __init__(self, msg):
        super().__init__(msg=msg)


class GetDownloadLinksException(PluginException):
    """
    If something wents wrong while getting the links.
    """

    def __init__(self, msg):
        super().__init__(msg=msg)
