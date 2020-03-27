Hello World
===========

We will use the internal test plugin, to show how to develop a plugin for unidown.

Setup class
-----------

As already mentioned we have to subclass from :py:class:`unidown.plugin.a_plugin.APlugin`.

.. code-block:: python

    class Plugin(APlugin):
        _info = PluginInfo('test', '0.1.0', 'raw.githubusercontent.com')

Also we set some general information like name, version and our domain where we download from.

Now we have to implement the work the plugin has to do. For that we have to implement the following methods.

__init__(self, options: List[str] = None) :py:class:`~unidown.plugin.a_plugin.APlugin`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The options

_create_last_update_time(self) -> datetime :py:meth:`~unidown.plugin.a_plugin.APlugin._create_last_update_time`
    This will return one datetime what the newest update time is. For example your link collection gets updated every month, this time would be the date. If you dont know or want to check the links every time, return the current time (`datetime.now()`)

_create_download_links(self) -> Dict[str, LinkItem] :py:meth:`~unidown.plugin.a_plugin.APlugin._create_download_links`
    This is the core part of a plugin, this will invoke the link and time creation.

First you can setup a normal python like project by creating a `setup.py`. The name should begin with `unidown_` but must not.

More important is the entry point we have to set.

.. code-block:: python

    entry_points={
        'unidown.plugin': "test = unidown_test_plugin.plugin:Plugin"
    },

We hook use the entry point `unidown.plugin` to get discovered by unidown. `test` is the name of our plugin and the name it an be referenced.