#!/usr/bin/env python
"""
Setup.py for unidown.
"""

from pathlib import Path

from setuptools import find_packages, setup

from unidown import static_data

# get long description
with Path('README.rst').open(mode='r', encoding='UTF-8') as reader:
    LONG_DESCRIPTION = reader.read()

setup(
    name=static_data.NAME,
    version=static_data.VERSION,
    description=static_data.DESCRIPTION,
    long_description=LONG_DESCRIPTION,
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
    python_requires='>=3.8',
    install_requires=[
        'urllib3[secure]==1.25.8',
        'tqdm==4.44.0',
        'packaging==20.3',
    ],
    extras_require={
        'dev': [
            'flake8==3.7.9',
            'pylint==2.4.4',
            'pyroma==2.6',
            'pytest==5.4.1',
            'pytest-cov==2.8.1',
            'Sphinx==2.4.4',
            'sphinx-autodoc-typehints==1.10.3',
            'sphinx_rtd_theme==0.4.3',
            'twine==3.1.1',
            'setuptools==46.1.3',
            'wheel==0.34.2',
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
