.ONESHELL:
.PHONY: $(MAKECMDGOALS)
##
##    🚧 PyTezos developer tools
##
##  DEV=1               Whether to install dev dependencies
DEV=1
##  TAG=latest          Tag for the `image` command
TAG=latest

##

help:              ## Show this help (default)
	@grep -Fh "##" $(MAKEFILE_LIST) | grep -Fv grep -F | sed -e 's/\\$$//' | sed -e 's/##//'

all:               ## Run a whole CI pipeline: lint, run tests, build docs
	make install lint test docs

install-deps:      ## Install binary dependencies
ifneq (,$(findstring linux-gnu,$(OSTYPE)))
	sudo apt install libsodium-dev libgmp-dev pkg-config
else ifneq (,$(findstring darwin,$(OSTYPE)))
	brew install libsodium gmp pkg-config
else
	echo "Unsupported platform $(OSTYPE)"
	exit 1
endif

install:           ## Install project dependencies
	poetry install \
	`if [ "${DEV}" = "0" ]; then echo "--no-dev"; fi`

lint:              ## Lint with all tools
	make isort black ruff mypy

test:              ## Run test suite
	# FIXME: https://github.com/pytest-dev/pytest-xdist/issues/385#issuecomment-1177147322
	poetry run sh -c "pytest --cov-report=term-missing --cov=pytezos --cov=michelson_kernel --cov-report=xml -n auto -s -v tests/contract_tests tests/integration_tests tests/unit_tests && pytest -xv tests/sandbox_tests"

test-ci:
	poetry run sh -c "pytest --junitxml="unit_test_results.xml" -sv tests/unit_tests"
	poetry run sh -c "pytest --junitxml="contract_test_results.xml" -sv tests/contract_tests"
	poetry run sh -c "pytest --junitxml="integration_test_results.xml" -sv tests/integration_tests"
ifneq (,$(findstring linux-gnu,$(OSTYPE)))
	poetry run sh -c "pytest --junitxml="sandbox_test_results.xml" -xv tests/sandbox_tests"
endif

docs:              ## Build docs
	make kernel-docs rpc-docs
	cd docs
	rm -r build || true
	poetry run make html
	cd ..

##

isort:             ## Format with isort
	poetry run isort src tests scripts

black:             ## Format with black
	poetry run black src tests scripts --exclude ".*/docs.py"

ruff:              ## Lint with ruff
	poetry run ruff check src tests scripts

mypy:              ## Lint with mypy
	poetry run mypy src scripts tests

cover:             ## Print coverage for the current branch
	poetry run diff-cover --compare-branch `git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'` coverage.xml

build:             ## Build Python wheel package
	poetry build

image:             ## Build Docker image
	docker buildx build . --file pytezos.dockerfile -t pytezos:${TAG} --load
	docker buildx build . --file michelson-kernel.dockerfile -t michelson-kernel:${TAG} --load

clean:             ## Remove all files from .gitignore except for `.venv`
	git clean -xdf --exclude=".venv"

update:            ## Update dependencies, export requirements.txt
	poetry update

	cp pyproject.toml pyproject.toml.bak
	cp poetry.lock poetry.lock.bak

	poetry export --without-hashes -o requirements.txt
	poetry export --without-hashes -o requirements.dev.txt --with dev
	poetry remove notebook
	poetry export --without-hashes -o requirements.slim.txt

	mv pyproject.toml.bak pyproject.toml
	mv poetry.lock.bak poetry.lock

	make install

##

install-kernel:    ## Install Michelson IPython kernel
	poetry run michelson-kernel install

remove-kernel:     ## Remove Michelson IPython kernel
	jupyter kernelspec uninstall michelson -f

notebook:          ## Run Jupyter notebook
	poetry run jupyter notebook

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
	poetry run python scripts/fetch_contract_data.py
	poetry run python scripts/generate_contract_tests.py
	# poetry run pytest -v tests/contract_tests

kernel-docs:       ## Build docs for Michelson IPython kernel
	poetry run python scripts/generate_kernel_docs.py

# NOTE: See `pytezos.sandbox.parameters`
sandbox-params:
	docker pull tezos/tezos:master
	docker create --name temp tezos/tezos:master
	docker cp temp:/usr/local/share/tezos/023-PtSeouLo-parameters src/pytezos/sandbox/
	docker rm temp

rpc-docs:          ## Build docs for Tezos node RPC
	poetry run python scripts/fetch_rpc_docs.py

before_release:    ## Prepare for a new release after updating version in pyproject.toml
	make update all
