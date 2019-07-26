#!/bin/sh
# executed from project root

rm -rf ./build/doc/

sphinx-build -b html ./doc/source/ ./build/doc/html/
sphinx-build -b linkcheck ./doc/source/ ./build/doc/linkcheck/
sphinx-build -b latex ./doc/source/ ./build/doc/latex/

cd ./build/doc/latex/
lualatex --jobname="documentation" --interaction=nonstopmode --halt-on-error ./sphinx.tex
lualatex --jobname="documentation" --interaction=nonstopmode --halt-on-error ./sphinx.tex
cd ../../../
