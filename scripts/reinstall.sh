#!/bin/sh
# executed from project root

pip install --upgrade --no-cache .[dev]
cd testplugin
pip install --upgrade --no-cache .
cd ..
