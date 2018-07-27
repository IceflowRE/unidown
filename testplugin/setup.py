#!/usr/bin/env python
from setuptools import find_packages, setup

from unidown import static_data

setup(
    name="Unidown test plugin",
    version="0.1.0",
    description=static_data.DESCRIPTION,
    author="Iceflower S",
    author_email="iceflower@gmx.de",
    license='GPLv3',
    packages=find_packages(),
    python_requires='>=3.6',
    zip_safe=True,
    entry_points={
        'unidown.plugins': "test = testplugin.plugin:Plugin"
    },
)
