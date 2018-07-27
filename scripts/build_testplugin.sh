#!/bin/sh
# executed from project root

py_version="$1"

echo $(python --version)
cd ./testplugin
python setup.py clean --all
python setup.py bdist_wheel --python-tag "$py_version"
cd ../
