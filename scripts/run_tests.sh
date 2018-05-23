#!/bin/sh
# executed from project root

echo $(python --version)

prospector --profile ./.prospector.yaml

echo ""
echo "NOSE 2"
echo "----------------------------------------------------------------------"
nose2 -c setup.cfg -v
