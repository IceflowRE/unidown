#!/bin/sh
# executed from project root

py_version="$1"

./scripts/createProtoClasses.sh

python setup.py clean --all
python setup.py bdist_wheel --python-tag "$py_version"

sphinx-build -b html -b linkcheck ./doc/source/ ./doc/build/
