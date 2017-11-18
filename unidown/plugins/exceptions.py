"""
Default exceptions of plugins.
"""


class PluginException(Exception):
    """
    Base class for exceptions in a plugin.
    If catching this, it implicit that the plugin is unable to work further.

    :ivar msg: exception message
    :vartype msg: str
    """

    def __init__(self, msg=''):
        self.msg = msg
