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
	cram tests/*.t

itest:
	cram -i tests/*.t
