#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name='flake8-pylint-ext',
    version='1.0.0',
    description='flake8 plugin with all extensions enabled',
    author='Gram, Iceflower',
    author_email='gram@orsinium.dev, iceflower@gmx.de',
    license='MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords='flake8 plugin extension pylint introspection linter',
    packages=find_packages(include=['flake8_pylint_ext', 'flake8_pylint_ext.*']),
    python_requires='>=3.8',
    install_requires=[
        'flake8',
        'pylint',
    ],
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'flake8.extension': [
            'PL = flake8_pylint_ext:PyLintExt',
        ],
    },
)
