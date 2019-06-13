#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages, setup

from unidown import static_data

# get long description
with Path('README.rst').open(mode='r', encoding='UTF-8') as reader:
    long_description = reader.read()

setup(
    name=static_data.NAME,
    version=static_data.VERSION,
    description=static_data.DESCRIPTION,
    long_description=long_description,
    author=static_data.AUTHOR,
    author_email=static_data.AUTHOR_EMAIL,
    license='GPLv3',
    url=static_data.PROJECT_URL,
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Environment :: Console',
        # 'Environment :: X11 Applications :: Qt',
    ],
    keywords='modular downloader',
    packages=find_packages(include=['unidown', 'unidown.*']),
    python_requires='>=3.7',
    install_requires=[
        'urllib3[secure]==1.25.3',
        'tqdm==4.32.1',
        'protobuf==3.8.0',
        'packaging==19.0',
    ],
    extras_require={
        'dev': [
            'prospector[with_everything]==1.1.6.4',
            'nose2[coverage_plugin]==0.9.1',
            'Sphinx==2.1.1',
            'sphinxcontrib-svg2pdfconverter==0.1.0',
            'sphinx_rtd_theme==0.4.3',
            'twine==1.13.0',
            'setuptools==41.0.1',
            'wheel==0.33.4',
        ],
    },
    package_data={

    },
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'unidown = unidown.main:main',
        ],
        # 'gui_scripts': [
        #    '???',
        # ],
    },
)
