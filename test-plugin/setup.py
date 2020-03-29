#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name="unidown_test",
    version="0.1.0",
    description="Test plugin for unidown.",
    author="Iceflower S",
    author_email="iceflower@gmx.de",
    license='MIT',
    packages=find_packages(include=['unidown_test', 'unidown_test.*']),
    python_requires='>=3.8',
    install_requires=[
        'unidown==2.0.0.dev7',
    ],
    zip_safe=True,
    entry_points={
        'unidown.plugin': "test = unidown_test.plugin:Plugin"
    },
)
