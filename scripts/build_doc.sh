#!/bin/sh
# executed from project root

rm -rf ./doc/build/

sphinx-build -b html ./doc/source/ ./doc/build/html/
sphinx-build -b linkcheck ./doc/source/ ./doc/build/linkcheck/
sphinx-build -b latex ./doc/source/ ./doc/build/latex/

cd ./doc/build/latex/
lualatex --jobname="documentation" --interaction=nonstopmode --halt-on-error ./sphinx.tex
lualatex --jobname="documentation" --interaction=nonstopmode --halt-on-error ./sphinx.tex
cd ../../../
