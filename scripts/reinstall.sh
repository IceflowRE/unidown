#!/bin/sh
# executed from project root

py_version="$1"
app_version=$(grep -oP "VERSION\s=\s'\K\w+.\w+.\w+" ./unidown/core/data/static.py)

./scripts/build.sh "$py_version"
pip install --upgrade --force-reinstall --no-cache ./dist/Universal_Downloader-"$app_version"-"$py_version"-none-any.whl[dev]
