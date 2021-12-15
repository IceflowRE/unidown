Structure
=========

Variables
---------

_INFO
    information about the plugin, must be set everytime

_SAVESTATE_CLS
    must be set if a custom SaveState format is in use

_simul_downloads
    adjust it to a low value to reduce the load on the target server

_options
    options, passed by the command line, ``delay`` will be set to 0 in absence of a value, set it to a higher value to reduce the load on the target server

_unit
    unit displayed while downloading

Methods
-------

_create_last_update_time
    returns the update time of the complete data e.g. the newest item in the collection
    If for some reasons its not easily collectable or not available or want to check the links every time, return the current time.

_create_download_data
    returns a LinkItemDict, with links and their update time

_load_default_options
    override if you need your own default options

load_savestate
    override if you have your own custom savestate

update_savestate
    override if you have your own custom savestate

LinkItemDict
------------

The LinkItemDict is an essential part of unidown. It is a normal dictionary with some special function.
The key is the link as a string. The value is a LinkItem.

LinkItem
--------

LinkItem has two essential values ``name`` and ``time``, the used name is at the same time the file given at downloading.
