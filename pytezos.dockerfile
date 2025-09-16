FROM python:3.12-alpine3.22 AS compile-image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apk add --update --no-cache \
	build-base \
	libtool \
	autoconf \
	automake \
	python3-dev \
	libffi-dev \
	gmp-dev \
	libsodium-dev

RUN python -m venv --without-pip --system-site-packages /opt/pytezos \
    && mkdir -p /opt/pytezos/src/pytezos/ \
    && touch /opt/pytezos/src/pytezos/__init__.py \
    && mkdir -p /opt/pytezos/src/michelson_kernel/ \
    && touch /opt/pytezos/src/michelson_kernel/__init__.py
WORKDIR /opt/pytezos
ENV PATH="/opt/pytezos/bin:$PATH"
ENV PYTHON_PATH="/opt/pytezos/src:$PATH"

COPY pyproject.toml requirements.slim.txt README.md /opt/pytezos/

RUN uv pip install --prefix /opt/pytezos --no-cache-dir --disable-pip-version-check --no-deps -r /opt/pytezos/requirements.slim.txt -e .

FROM python:3.12-alpine3.22 AS build-image
RUN apk add --update --no-cache \
	binutils \
	gmp-dev \
	libsodium-dev

RUN adduser -D pytezos
USER pytezos
ENV PATH="/opt/pytezos/bin:$PATH"
ENV PYTHONPATH="/home/pytezos:/home/pytezos/src:/opt/pytezos/src:/opt/pytezos/lib/python3.12/site-packages:$PYTHONPATH"
WORKDIR /home/pytezos/
ENTRYPOINT ["python"]

COPY --chown=pytezos --from=compile-image /opt/pytezos /opt/pytezos
COPY --chown=pytezos . /opt/pytezos
