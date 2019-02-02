#!/usr/bin/env python
from setuptools import find_packages, setup

from unidown import static_data

setup(
    name="unidown_test_plugin",
    version="0.1.0",
    description=static_data.DESCRIPTION,
    author="Iceflower S",
    author_email="iceflower@gmx.de",
    license='GPLv3',
    packages=find_packages(),
    python_requires='>=3.7',
    zip_safe=True,
    entry_points={
        'unidown.plugin': "test = unidown_test_plugin.plugin:Plugin"
    },
)
