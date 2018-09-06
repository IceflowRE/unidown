#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages, setup

# get long description
with Path('README.md').open(mode='r', encoding='UTF-8') as reader:
    long_description = reader.read()

setup(
    name='unidown',
    version='1.2.3',
    description='MR ebook downloader.',
    long_description=long_description,
    author='Iceflower S',
    author_email='iceflower@gmx.de',
    license='GPLv3',
    url='https://github.com/IceflowRE/unidown',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Environment :: Console',
        # 'Environment :: X11 Applications :: Qt',
    ],
    keywords='modular downloader',
    packages=find_packages(include=['unidown', 'unidown.*']),
    python_requires='>=3.6',
    install_requires=[
        'urllib3[secure]==1.23',
    ],
    extras_require={
        'dev': [
            'nose2[coverage_plugin]==0.8.0',
            'twine==1.11.0',
            'setuptools==40.2.0',
            'wheel==0.31.1',
        ],
    },
    package_data={

    },
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'unidown = unidown.StartDeDownload',
        ],
    },
)
