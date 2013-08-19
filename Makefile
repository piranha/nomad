PWD = $(shell pwd)

PYVER = $(shell python -V 2>&1 | cut -c8)
ifeq ($(PYVER), 3)
PY3 = 1
endif

.PHONY: help docs test itest

help:
	@echo "Use \`make <target>\` with one of targets:"
	@echo "  docs  build docs"
	@echo "  open  open docs"
	@echo "  test  run tests"

docs:
	cd docs && make

open:
	cd docs && make open

test:
ifdef PY3
	rm -rf _py3
	mkdir -p _py3
	cp -a nomad _py3/nomad
	2to3 -x import -n -w _py3/nomad
	2to3 -x import -n -w -d _py3/nomad
	python _py3/nomad/utils.py
	PYTHONPATH=$(PWD)/_py3 NOMAD="python $(PWD)/_py3/nomad/__init__.py" cram tests/*.t
else
	python nomad/utils.py
	PYTHONPATH=$(PWD) NOMAD="python $(PWD)/nomad/__init__.py" cram --keep-tmpdir tests/*.t
#	cram tests/*.t
endif

itest:
	cram -i tests/*.t
