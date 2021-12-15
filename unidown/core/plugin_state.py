from enum import IntEnum


class PluginState(IntEnum):
    """
    State of a plugin, after it ended or was not found.
    """
    #: successfully end
    EndSuccess = 0
    #: :class:`~unidown.plugin.exceptions.PluginException` was raised.
    RunFail = 1
    #: Exception was raised but not :class:`~unidown.plugin.exceptions.PluginException`.
    RunCrash = 2
    #: Exception was raised while loading/ initializing.
    LoadCrash = 3
    #: Plugin was not found.
    NotFound = 4
