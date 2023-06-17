# convenient makefile

SHELL	= /bin/bash
.ONESHELL:

MODULE	= CacheToolsUtils
F.md	= $(wildcard *.md)
F.pdf	= $(F.md:%.md=%.pdf)


# cleanup and environment

.PHONY: clean clean-venv
clean:
	$(RM) -r __pycache__ *.egg-info dist build .mypy_cache .pytest_cache htmlcov
	$(RM) .coverage $(F.pdf)

clean.venv: clean
	$(RM) -r venv

# venv for local testing
PYTHON	= python
PIP		= venv/bin/pip

venv:
	$(PYTHON) -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev,pub,tests]

#
# Tests
#
PYTEST	= pytest --log-level=debug --capture=tee-sys
PYTOPT	=

.PHONY: check
check: check.mypy check.flake8 check.pytest check.coverage check.pymarkdown

.PHONY: check.mypy
check.mypy:
	. venv/bin/activate
	mypy $(MODULE).py

.PHONY: check.flake8
check.flake8:
	. venv/bin/activate
	flake8 --ignore=E227,E501 $(MODULE).py

.PHONY: check.black
check.black:
	. venv/bin/activate
	black --check $(MODULE).py

.PHONY: check.pytest
check.pytest:
	. venv/bin/activate
	$(PYTEST) $(PYTOPT) test.py

.PHONY: check.coverage
check.coverage:
	. venv/bin/activate
	coverage run -m $(PYTEST) $(PYTOPT) test.py
	coverage html $(MODULE).py
	coverage report --fail-under=100 --include=CacheToolsUtils.py

.PHONY: check.pymarkdown
check.pymarkdown:
	. venv/bin/activate
	pymarkdown scan *.md

.PHONY: install
install: $(MODULE).egg-info
	type $(PYTHON)

$(MODULE).egg-info: venv
	$(PIP) install -e .

# generate source and built distribution
dist:
	$(PYTHON) -m build

.PHONY: publish
publish: dist
	# provide pypi login/pw or token somewhere…
	echo twine upload dist/*

# generate pdf doc
MD2PDF  = pandoc -f markdown -t latex -V papersize:a4 -V geometry:hmargin=2.5cm -V geometry:vmargin=3cm

%.pdf: %.md
	$(MD2PDF) -o $@ $<
