#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="unidown_test_plugin",
    version="0.1.0",
    description="Test plugin for unidown.",
    author="Iceflower S",
    author_email="iceflower@gmx.de",
    license='GPLv3',
    packages=find_packages('unidown_test_plugin', 'unidown_test_plugin.*'),
    python_requires='>=3.7',
    install_requires=[
        'unidown',
    ],
    zip_safe=True,
    entry_points={
        'unidown.plugin': "test = unidown_test_plugin.plugin:Plugin"
    },
)
