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
    long_description_content_type='text/x-rst',
    author=static_data.AUTHOR,
    author_email=static_data.AUTHOR_EMAIL,
    license='GPLv3',
    url=static_data.PROJECT_URL,
    classifiers=[
        'Programming Language :: Python :: 3.8',
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
        'urllib3[secure]==1.25.8',
        'tqdm==4.35.0',
        'packaging==19.1',
    ],
    extras_require={
        'dev': [
            'prospector[with_everything]==1.2.0',
            'pytest==5.4.1',
            'pytest-cov==2.8.1',
            'coverage==5.0.3',
            'Sphinx==2.2.0',
            'sphinx-autodoc-typehints==1.7.0',
            'sphinx_rtd_theme==0.4.3',
            'twine==1.14.0',
            'setuptools==41.2.0',
            'wheel==0.33.6',
        ],
    },
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
