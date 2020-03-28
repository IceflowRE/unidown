.. _usage-label:

Using UniDown
=============

The program is a terminal program, so it runs from the terminal.

Calling with:

.. code-block:: none

    unidown

Furthermore, there are additional arguments:

.. option:: -h, --help

    show this help message and exit

.. option:: -v, --version

    show program's version number and exit

.. option:: --list-plugins

    show plugin list and exit

.. option:: -p name, --plugin name

    plugin to execute

.. option::-r path, --root path  main directory where all files will be created (default: ./)

    main directory where all files will be created

.. option:: -o option [option ...], --option option [option ...]

    options passed to the plugin, e.g. `-o username=South American coati -o password=Nasua Nasua`

.. option:: --logfile path

    log filepath relativ to the main dir (default: ./unidown.log)

.. option:: -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}

    set the logging level (default: INFO)
