#!/bin/sh
# executed from project root

py_version="$1"
app_version=$(grep -oP "VERSION\s=\s'\K([\w\W]*)'" ./unidown/static_data.py)
app_version=${app_version:: -1}

./scripts/build.sh "$py_version"
pip install --upgrade --no-cache ./dist/unidown-"$app_version"-"$py_version"-none-any.whl[dev]
./scripts/build_testplugin.sh "$py_version"
pip install --upgrade --no-cache ./testplugin/dist/unidown_test_plugin-0.1.0-"$py_version"-none-any.whl
