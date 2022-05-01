*********
Changelog
*********

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Versions before 2.1.0 are not documented.

2.1.0
=====

Breaking Changes
----------------

- Removed ``__version__`` in ``__init__.py``
- Renamed ``PluginException`` to  ``PluginError``
- Renamed ``PluginState`` enums to uppercase
- Moved ``get_plugins()`` to module level out of ``APlugin``
