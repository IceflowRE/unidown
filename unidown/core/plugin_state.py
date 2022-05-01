from enum import IntEnum


class PluginState(IntEnum):
    """
    State of a plugin, after it ended or was not found.
    """

    #: successfully end
    END_SUCCESS = 0
    #: :class:`~unidown.plugin.exceptions.PluginError` was raised.
    RUN_FAIL = 1
    #: Exception was raised but not :class:`~unidown.plugin.exceptions.PluginError`.
    RUN_CRASH = 2
    #: Exception was raised while loading/ initializing.
    LOAD_CRASH = 3
    #: Plugin was not found.
    NOT_FOUND = 4
