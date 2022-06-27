.ONESHELL:
.PHONY: docs
.DEFAULT_GOAL: all


LINT_TARGETS ?= \
	src \
	scripts \

DEV ?= 1

all: install lint test cover

update:
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/metadata-schema.json -O src/pytezos/contract/metadata-schema.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-000.json -O tests/unit_tests/test_contract/metadata/example-000.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-001.json -O tests/unit_tests/test_contract/metadata/example-001.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-002.json -O tests/unit_tests/test_contract/metadata/example-002.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-003.json -O tests/unit_tests/test_contract/metadata/example-003.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-004.json -O tests/unit_tests/test_contract/metadata/example-004.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-005.json -O tests/unit_tests/test_contract/metadata/example-005.json

	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-21/metadata-schema.json -O src/pytezos/contract/token_metadata-schema.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-21/examples/example-000-base.json -O tests/unit_tests/test_contract/token_metadata/example-000-base.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-21/examples/example-010-fungible-tz21.json -O tests/unit_tests/test_contract/token_metadata/example-010-fungible-tz21.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-21/examples/example-020-digital-collectible.json -O tests/unit_tests/test_contract/token_metadata/example-020-digital-collectible.json


install:
	git submodule update --init  || true
	poetry install `if [ "${DEV}" = "0" ]; then echo "--no-dev"; fi`

install-kernel:
	poetry run python -m michelson_kernel install

remove-kernel:
	jupyter kernelspec uninstall michelson -f

notebook:
	PYTHONPATH="$$PYTHONPATH:src" poetry run jupyter notebook

debug:
	pip install . --force --no-deps

isort:
	poetry run isort ${LINT_TARGETS}

black:
	poetry run black ${LINT_TARGETS}

pylint:
	poetry run pylint ${LINT_TARGETS} || poetry run pylint-exit $$?

mypy:
	poetry run mypy ${LINT_TARGETS}

lint: isort black pylint mypy

test:
	poetry run pytest --cov-report=term-missing --cov=pytezos --cov=michelson_kernel --cov-report=xml tests

cover:
	poetry run diff-cover coverage.xml

build:
	poetry build

image:
	docker build . -t bakingbad/pytezos:latest

docs:
	poetry run sh -c "cd docs && rm -rf ./build && $(MAKE) html && cd .."

kernel-docs:
	poetry run python scripts/gen_kernel_docs_py.py

rpc-docs:
	poetry run python scripts/fetch_docs.py

release-patch:
	bumpversion patch
	git push --tags
	git push

release-minor:
	bumpversion minor
	git push --tags
	git push

release-major:
	bumpversion major
	git push --tags
	git push

update-contract-tests:
	poetry run python scripts/fetch_contract_data.py
	poetry run python scripts/generatecontract_tests.py