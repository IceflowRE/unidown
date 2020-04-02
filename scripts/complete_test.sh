# executed from project root

pip install --upgrade .
cd test-plugin
pip install --upgrade .
cd ..

python setup.py clean --all
python setup.py bdist_wheel

flake8 ./unidown
pylint --rcfile=setup.cfg ./unidown/ || true
pyroma .

pytest -v --cov-config=setup.cfg --cov=cmt --cov-report term --cov-report=xml --cov-report html
python setup.py check -v -m -s
twine check dist/*

sphinx-build -b html -j auto -T -E -a ./doc/ ./build/doc/html/
sphinx-build -b linkcheck ./doc/ ./build/doc/linkcheck/
