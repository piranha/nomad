PWD = $(shell pwd)
VERSION = $(shell grep '__version__ =' nomad/__init__.py | cut -d ' ' -f 3 | tr -d "'")

#TEST_ARGS ?= --keep-tmpdir

.PHONY: help docs test itest

help:
	@echo "Use \`make <target>\` with one of targets:"
	@echo "  docs  build docs"
	@echo "  open  open docs"
	@echo "  test  run tests"
	@echo "  pub   publish to PyPI"

docs:
	cd docs && make

open:
	cd docs && make open


test:
	test -d .env && source .env/bin/activate; \
	python nomad/utils.py; \
	PYTHONPATH=$(PWD) NOMAD="python $(PWD)/nomad/__init__.py" prysk $(TEST_ARGS) tests/*.t

itest:
	test -d .env && source .env/bin/activate; \
	PYTHONPATH=$(PWD) NOMAD="python $(PWD)/nomad/__init__.py" prysk -i $(TEST_ARGS) tests/*.t

pub:
	pip install -q build
	python3 -m build
	twine upload dist/nomad-$(VERSION).tar.gz


.env: requirements-dev.txt
	test -d $@ || python3 -m venv $@
	.env/bin/pip install -r requirements-dev.txt
	@touch $@
