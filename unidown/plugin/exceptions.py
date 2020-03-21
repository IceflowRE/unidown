"""
Default exceptions of plugins.
"""


class PluginException(Exception):
    """
    Base class for exceptions in a plugin.
    If catching this, it implicit that the plugin is unable to work further.

    :param msg: message

    :ivar msg: exception message
    """

    def __init__(self, msg: str = ''):
        super().__init__(msg)
        self.msg: str = msg
