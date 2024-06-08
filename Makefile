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


test: .env
	source .env/bin/activate; \
	python nomad/utils.py; \
	PYTHONPATH=$(PWD) NOMAD="python $(PWD)/nomad/__init__.py" prysk $(TEST_ARGS) tests/*.t

itest: .env
	source .env/bin/activate; \
	PYTHONPATH=$(PWD) NOMAD="python $(PWD)/nomad/__init__.py" prysk -i $(TEST_ARGS) tests/*.t

pub: .env
	source .env/bin/activate; \
	pip install -q build twine; \
	python -m build; \
	twine upload dist/nomad-$(VERSION).tar.gz dist/nomad-$(VERSION)-py3-none-any.whl

.env: pyproject.toml
	test -d $@ || python3 -m venv $@
	.env/bin/pip install .[test]
	@touch $@
