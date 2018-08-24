from enum import Enum


class PluginState(Enum):
    """
    State of a plugin, after it ended or was not found.
    """
    END_SUCCESS = 0  #: successfully end
    RUN_FAIL = 1  #: raised an ~unidown.plugin.exceptions.PluginException
    RUN_CRASH = 2  #: raised an exception but ~unidown.plugin.exceptions.PluginException
    LOAD_CRASH = 3  #: raised an exception while loading/ initializing
    NOT_FOUND = 4  #: plugin was not found
