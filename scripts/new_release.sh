#!/bin/sh
# executed from project root

app_version=$(grep -oP "VERSION\s=\s'\K([\w\W]*)'" ./unidown/core/data/static.py)
app_version=${app_version:: -1}

# change online version for updater
echo "$app_version" > ./version
