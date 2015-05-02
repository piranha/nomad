PWD = $(shell pwd)
TEST_ARGS ?= --keep-tmpdir

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
	python nomad/utils.py
	PYTHONPATH=$(PWD) NOMAD="python $(PWD)/nomad/__init__.py" cram $(TEST_ARGS) tests/*.t

itest:
	cram -i tests/*.t

pub:
	python setup.py sdist upload
