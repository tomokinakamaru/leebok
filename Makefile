.PHONY: default
default: setup

.PHONY: all
all: setup

.PHONY: setup
setup: venv/bin/flake8 venv/bin/mypy
	venv/bin/pip install .

.PHONY: clean
clean:
	rm -rf .leebok
	rm -rf .coverage .coverage.* venv .tox htmlcov src/*.egg-info
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

venv:
	python3 -m venv venv --without-pip

venv/bin/pip: venv
	curl -sfS https://bootstrap.pypa.io/get-pip.py | venv/bin/python

venv/bin/flake8: venv/bin/pip
	venv/bin/pip install flake8

venv/bin/mypy: venv/bin/pip
	venv/bin/pip install mypy
