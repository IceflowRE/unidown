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
        'Programming Language :: Python :: 3.10',
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
    python_requires='>=3.10',
    install_requires=[
        'urllib3[secure]>=1.26.12',
        'tqdm>=4.64.1',
        'packaging>=21.3',
    ],
    extras_require={
        'doc': [
            'Sphinx>=5.1.1',
            'sphinx-autodoc-typehints>=1.19.2',
            'sphinx_rtd_theme>=1.0.0',
            'sphinxcontrib-mermaid>=0.7.1',
        ],
        'dev': [
            'flake8',
            # flake8 extensions start
            'wemake-python-styleguide',
            'flake8-2020',
            'flake8-builtins',
            'flake8-comprehensions',
            'flake8-docstrings',
            'flake8-multiline-containers',
            'flake8-use-fstring',
            'flake8-simplify',
            # flake8 extensions end
            'mypy',
            'types-certifi',
            'types-urllib3',
            'types-setuptools',
            'pylint',
            'pyroma',
            'pytest>=7.1.3',
            'pytest-cov>=3.0.0',
            'setuptools',
            'twine>=4.0.1',
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
