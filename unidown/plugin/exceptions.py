"""
Default exceptions of plugins.
"""


class PluginError(Exception):
    """
    Base class for exceptions in a plugin.
    If catching this, it is implicit that the plugin is unable to work further.

    :param msg: message
    """

    def __init__(self, msg: str = '') -> None:
        super().__init__(msg)
        #: Exception message.
        self.msg: str = msg
