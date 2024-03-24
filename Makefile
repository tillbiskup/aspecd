# Minimal Makefile for automating recurring tasks during development
#
# Copyright (c) 2023, Till Biskup
# 2023-12-06

.PHONY: docs tests help
.DEFAULT_GOAL := help

help:
	@echo "This makefile automates different recurring tasks"
	@echo ""
	@echo "The following targets are available:"
	@echo ""
	@echo "docs  - create documentation using Sphinx"
	@echo "tests - run unittests"
	@echo "check - check code using prospector"
	@echo "black - format code using Black"

docs:
	@echo "Create documentation using Sphinx"
	$(MAKE) -C docs html

tests:
	@echo "Run unittests"
	cd tests/ && python -m unittest discover -s . -t .

check:
	@echo "Check code using prospector... this may take a while"
	prospector

black:
	@echo "Automatically format code using Black"
	black -l 78 . --extend-exclude templates
