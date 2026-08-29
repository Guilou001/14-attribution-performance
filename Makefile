# Prérequis : uv
UV ?= uv

setup:
	$(UV) sync --locked --all-extras

test:             ## 9 groupes de tests fermés, sans réseau
	$(UV) run pytest

lint:
	$(UV) run ruff check src tests

all:              ## fetch + attribute + gips
	$(UV) run perf fetch
	$(UV) run perf attribute
	$(UV) run perf gips
