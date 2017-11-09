#!/usr/bin/env python
from setuptools import find_packages, setup

import unidown.core.data.static as static_data

setup(
    name=static_data.NAME,
    version=static_data.VERSION,
    description='Universal downloader, a modular extensible downloader who manage progress and updates.',
    author=static_data.AUTHOR,
    author_email=static_data.AUTHOR_EMAIL,
    license='GPLv3',
    url=static_data.PROJECT_URL,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Natural Language :: German',
        'Environment :: Console',
        # 'Environment :: X11 Applications :: Qt',
    ],
    keywords='modular downloader',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'urllib3',
        'certifi',
        'tqdm',
        'protobuf',
        'packaging',
    ],
    extras_require={
        'dev': [
            'prospector[with_everything]',
            'cov-core',
            'codecov',
            'nose2',
            'Sphinx',
            'twine',
            'wheel',
        ],
    },
    package_data={

    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'unidown = unidown.core.main:main',
        ],
        # 'gui_scripts': [
        #    '???',
        # ],
    },
)
