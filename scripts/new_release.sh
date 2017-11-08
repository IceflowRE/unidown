#!/bin/sh
# executed from project root

app_version=$(grep -oP "VERSION\s=\s'\K\w+.\w+.\w+" ./unidown/core/data/static.py)

# change online version for updater
echo -e "$app_version""\c" > ./version
