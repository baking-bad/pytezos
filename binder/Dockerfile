FROM python:3.12-slim-bookworm

ARG NB_USER=mickey
ARG NB_UID=1000

USER root

RUN apt update && \
    apt install -y build-essential pkg-config libsodium-dev libgmp-dev && \
    rm -rf /var/lib/apt/lists/*

COPY . /tmp/pytezos
RUN pip install notebook jupyter-client /tmp/pytezos
RUN michelson-kernel install

ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

COPY binder/*.ipynb ${HOME}/
RUN chown -R ${NB_USER}:${NB_USER} ${HOME}/

WORKDIR ${HOME}
USER ${USER}

EXPOSE 8888
ENTRYPOINT []
