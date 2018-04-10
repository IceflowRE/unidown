#!/usr/bin/env python
from setuptools import find_packages, setup

import unidown.core.data.static as static_data

setup(
    name=static_data.NAME,
    version=static_data.VERSION,
    description=static_data.DESCRIPTION,
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
    packages=find_packages(include=['unidown']),
    python_requires='>=3.6',
    install_requires=[
        'urllib3[secure]==1.22',
        'tqdm==4.19.8',
        'protobuf==3.5.2.post1',
        'packaging==17.1',
    ],
    extras_require={
        'dev': [
            'prospector[with_everything]==0.12.7',  # if update, update config too: pep8 -> pycodestyle & pep257 -> pydocstyle
            'nose2[coverage_plugin]==0.7.4',
            'Sphinx==1.7.2',
            'sphinx_rtd_theme==0.2.5b2',
            'twine==1.11.0',
            'wheel==0.30.0',
        ],
    },
    package_data={

    },
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'unidown = unidown.core.main:main',
        ],
        # 'gui_scripts': [
        #    '???',
        # ],
    },
)
