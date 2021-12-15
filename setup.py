#!/usr/bin/env python
"""
Setup.py for unidown.
"""

from pathlib import Path

from setuptools import find_packages, setup

from unidown import meta

# get long description
with Path('README.rst').open(mode='r', encoding='UTF-8') as reader:
    LONG_DESCRIPTION = reader.read()

setup(
    name=meta.NAME,
    version=meta.VERSION,
    description=meta.DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    author=meta.AUTHOR,
    author_email=meta.AUTHOR_EMAIL,
    license='GPLv3',
    url=meta.PROJECT_URL,
    classifiers=[
        'Programming Language :: Python :: 3.8',
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
    python_requires='>=3.8',
    install_requires=[
        'urllib3[secure]>=1.26.7',
        'tqdm>=4.62.3',
        'packaging>=21.0',
    ],
    extras_require={
        'dev': [
            'flake8>=3.9.2',
            'pylint>=2.11.1',
            'pyroma>=3.2',
            'pytest>=6.2.5',
            'pytest-cov>=2.12.1',
            'setuptools>=58.2.0',
            'twine>=3.4.2',
            'wheel>=0.37.0',
            'Sphinx==4.3.0',
            'sphinx-autodoc-typehints==1.12.0',
            'sphinx_rtd_theme==1.0.0',
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
