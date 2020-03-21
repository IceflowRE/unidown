from enum import IntEnum


class PluginState(IntEnum):
    """
    State of a plugin, after it ended or was not found.
    """
    EndSuccess = 0  #: successfully end
    RunFail = 1  #: raised an ~unidown.plugin.exceptions.PluginException
    RunCrash = 2  #: raised an exception but ~unidown.plugin.exceptions.PluginException
    LoadCrash = 3  #: raised an exception while loading/ initializing
    NotFound = 4  #: plugin was not found
