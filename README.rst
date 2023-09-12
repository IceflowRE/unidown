********************
Universal Downloader
********************
|maintained| |programming language| |license|

|github actions| |readthedocs| |codecov|

|pypi|

----

unidown manages downloads and will only download items again when they are newer or not downloaded yet.

----

unidown is written with the main aspect on plugins. unidown itself can only manage the produced data from 3rd party plugins.

unidown saves all downloaded files with their modifications time and and will only download updated or not already downloaded files.

Find more information in the documentation at `Read the Docs <https://unidown.readthedocs.io/en/latest/index.html>`__.

----

Web
===

https://github.com/IceflowRE/unidown

Plugins
=======

mr_de
    - Crawl through german ebooks from Mobileread.
    - https://github.com/IceflowRE/unidown-mr_de

Credits
=======

- Developer
    - `Iceflower S <https://github.com/IceflowRE>`__
        - iceflower@gmx.de

Third Party
-----------

Packaging
    - Donald Stufft and individual contributors
    - https://github.com/pypa/packaging
    - `BSD-3-Clause, Apache-2.0 <https://github.com/pypa/packaging/blob/master/LICENSE>`__
tqdm
    - `noamraph <https://github.com/noamraph>`__
    - https://github.com/tqdm/tqdm
    - `MIT, MPL-2.0 <https://raw.githubusercontent.com/tqdm/tqdm/master/LICENCE>`__
urllib3
    - `Andrey Petrov and contributors <https://github.com/shazow/urllib3/blob/master/CONTRIBUTORS.txt>`__
    - https://github.com/shazow/urllib3
    - `MIT <https://github.com/shazow/urllib3/blob/master/LICENSE.txt>`__

License
-------

.. image:: http://www.gnu.org/graphics/gplv3-127x51.png
   :alt: GPLv3
   :align: center

Copyright (C) 2015-present Iceflower S

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

.. Badges.

.. |maintained| image:: https://img.shields.io/badge/maintained-yes-brightgreen.svg

.. |programming language| image:: https://img.shields.io/badge/language-Python_3.11-orange.svg
   :target: https://www.python.org/

.. |license| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0

.. |github actions| image:: https://img.shields.io/github/actions/workflow/status/IceflowRE/unidown/build.yml
   :target: https://github.com/IceflowRE/unidown/actions

.. |readthedocs| image:: https://readthedocs.org/projects/unidown/badge/?version=latest
   :target: https://unidown.readthedocs.io/en/latest/index.html

.. |pypi| image:: https://img.shields.io/pypi/v/unidown.svg
   :target: https://pypi.org/project/unidown/

.. |codecov| image:: https://img.shields.io/codecov/c/github/IceflowRE/unidown/main.svg?label=coverage
   :target: https://codecov.io/gh/IceflowRE/unidown
