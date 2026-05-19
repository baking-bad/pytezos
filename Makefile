.ONESHELL:
.PHONY: $(MAKECMDGOALS)
##
##    🚧 PyTezos developer tools
##
##  TAG=latest          Tag for the `image` command
TAG=latest

UNAME_S := $(shell uname -s)
##

help:              ## Show this help (default)
	@grep -Fh "##" $(MAKEFILE_LIST) | grep -Fv grep -F | sed -e 's/\\$$//' | sed -e 's/##//'

all:               ## Run a whole CI pipeline: lint, run tests, build docs
	make install lint test docs

install-deps:      ## Install binary dependencies
ifeq ($(UNAME_S),Linux)
	sudo apt install libsodium-dev libgmp-dev pkg-config
else ifeq ($(UNAME_S),Darwin)
	brew install libsodium gmp pkg-config
else
	echo "Unsupported platform $(UNAME_S)"
	exit 1
endif

install:           ## Install project dependencies
	uv sync --all-extras --all-groups --link-mode symlink --locked

lint:              ## Lint with all tools
	make isort black ruff mypy

test:              ## Run test suite
	# FIXME: https://github.com/pytest-dev/pytest-xdist/issues/385#issuecomment-1177147322
	uv run sh -c "pytest --cov-report=term-missing --cov=pytezos --cov=michelson_kernel --cov-report=xml -n auto -s -v tests/contract_tests tests/integration_tests tests/unit_tests && pytest -xv tests/sandbox_tests"

test-ci:
	uv run pytest --junitxml="unit_test_results.xml" -sv tests/unit_tests
	uv run pytest --junitxml="contract_test_results.xml" -sv tests/contract_tests
	uv run pytest --junitxml="integration_test_results.xml" -sv tests/integration_tests
ifeq ($(UNAME_S),Linux)
	uv run pytest --junitxml="sandbox_test_results.xml" -xv tests/sandbox_tests
endif

docs:              ## Build docs
	make kernel-docs rpc-docs
	cd docs
	rm -r build || true
	uv run make html
	cd ..

##

isort:             ## Format with isort
	uv run isort src tests scripts

black:             ## Format with black
	uv run black src tests scripts --exclude ".*/docs.py"

ruff:              ## Lint with ruff
	uv run ruff check src tests scripts

mypy:              ## Lint with mypy
	uv run mypy src scripts tests

cover:             ## Print coverage for the current branch
	uv run diff-cover --compare-branch `git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'` coverage.xml

build:             ## Build Python wheel package
	uv build

image:             ## Build Docker image
	docker buildx build . --file pytezos.dockerfile -t pytezos:${TAG} --load
	docker buildx build . --file michelson-kernel.dockerfile -t michelson-kernel:${TAG} --load

clean:             ## Remove all files from .gitignore except for `.venv`
	git clean -xdf --exclude=".venv"

update:            ## Update dependencies and regenerate uv.lock
	uv sync -U --all-extras --all-groups --link-mode symlink

##

install-kernel:    ## Install Michelson IPython kernel
	uv run michelson-kernel install

remove-kernel:     ## Remove Michelson IPython kernel
	jupyter kernelspec uninstall michelson -f

notebook:          ## Run Jupyter notebook
	uv run --extra jupyter jupyter notebook

##

update-tzips:      ## Update TZIP-16 schema and tests
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/metadata-schema.json -O src/pytezos/contract/metadata-schema.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-000.json -O tests/unit_tests/test_contract/metadata/example-000.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-001.json -O tests/unit_tests/test_contract/metadata/example-001.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-002.json -O tests/unit_tests/test_contract/metadata/example-002.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-003.json -O tests/unit_tests/test_contract/metadata/example-003.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-004.json -O tests/unit_tests/test_contract/metadata/example-004.json
	wget https://gitlab.com/tzip/tzip/-/raw/master/proposals/tzip-16/examples/example-005.json -O tests/unit_tests/test_contract/metadata/example-005.json

update-contracts:  ## Update contract tests
	uv run python scripts/fetch_contract_data.py
	uv run python scripts/generate_contract_tests.py
	# uv run pytest -v tests/contract_tests

kernel-docs:       ## Build docs for Michelson IPython kernel
	uv run python scripts/generate_kernel_docs.py

# NOTE: See `pytezos.sandbox.parameters`
sandbox-params:
	docker pull tezos/tezos:master
	docker create --name temp tezos/tezos:master
	docker cp temp:/usr/local/share/tezos/024-PtTALLiN-parameters src/pytezos/sandbox/
	docker rm temp

rpc-docs:          ## Build docs for Tezos node RPC
	uv run python scripts/fetch_rpc_docs.py

before_release:    ## Prepare for a new release after updating version in pyproject.toml
	make update all
