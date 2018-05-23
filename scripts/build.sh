#!/bin/sh
# executed from project root

py_version="$1"

./scripts/create_proto_classes.sh

echo $(python --version)
python setup.py clean --all
python setup.py bdist_wheel --python-tag "$py_version"
