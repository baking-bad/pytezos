# syntax=docker/dockerfile:1.7
FROM python:3.12-alpine3.22 AS compile-image
COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/

RUN apk add --update --no-cache \
	build-base \
	libtool \
	autoconf \
	automake \
	python3-dev \
	libffi-dev \
	gmp-dev \
	libsodium-dev

ENV UV_COMPILE_BYTECODE=1 \
	UV_LINK_MODE=copy \
	UV_NO_DEV=1 \
	UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install dependencies including the jupyter extra (cached layer)
RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=uv.lock,target=uv.lock \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
	--mount=type=bind,source=README.md,target=README.md \
	uv sync --locked --no-install-project --extra jupyter

# Install the project itself
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --locked --extra jupyter

FROM python:3.12-alpine3.22 AS build-image
RUN apk add --update --no-cache \
	binutils \
	gmp-dev \
	libsodium-dev

RUN adduser -D pytezos
USER pytezos
ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /home/pytezos/
ENTRYPOINT [ "/app/.venv/bin/jupyter-notebook", "--port=8888", "--ip=0.0.0.0", "--no-browser" ]
EXPOSE 8888

COPY --chown=pytezos --from=compile-image /app /app

RUN michelson-kernel install
