# PyTezos

[![Twitter](https://badgen.net/badge/icon/TezosBakingBad?icon=twitter&label=)](https://twitter.com/TezosBakingBad)
[![Monthly downloads](https://static.pepy.tech/badge/pytezos/month)](https://pepy.tech/project/pytezos)
[![GitHub stars](https://img.shields.io/github/stars/baking-bad/pytezos?color=2c2c2c&style=plain)](https://github.com/baking-bad/pytezos)
[![Python Version](https://img.shields.io/pypi/pyversions/pytezos?color=2c2c2c)](https://www.python.org)
<br>
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/baking-bad/pytezos/master?filepath=michelson_quickstart.ipynb)
[![License: MIT](https://img.shields.io/github/license/baking-bad/pytezos?color=2c2c2c)](https://github.com/baking-bad/pytezos/blob/next/LICENSE)
[![Latest release](https://img.shields.io/github/v/release/baking-bad/pytezos?label=version&color=2c2c2c)](https://github.com/baking-bad/pytezos/releases)
[![GitHub issues](https://img.shields.io/github/issues/baking-bad/pytezos?color=2c2c2c)](https://github.com/baking-bad/pytezos/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/baking-bad/pytezos?color=2c2c2c)](https://github.com/baking-bad/pytezos/pulls)

* RPC query engine
* Cryptography
* Building and parsing operations
* Smart contract interaction
* Local forging/packing & vice versa
* Working with Michelson AST

#### PyTezos CLI

* Generating contract parameter/storage schema
* Activating and revealing accounts
* Deploying contracts (+ GitHub integration)

#### Michelson REPL

* Builtin interpreter (reimplemented)
* Set of extra helpers (stack visualization, blockchain context mocking)

#### Michelson Jupyter kernel

* Custom interpreter with runtime type checker
* Syntax highlighting, autocomplete with `Tab`
* In-place docstrings with `Shift+Tab`
* Macros support
* Verbose execution logging
* Debug helpers

#### Michelson integration testing framework

* Writing integration tests using `unittest` package
* Simulating contract execution using remote intepreter (via RPC) or builtin one

## Installation

Make sure you have Python 3.9 to 3.13 installed and set as default in the system.  

You also need to install cryptographic packages before installing the library/building the project:

### Linux

#### Ubuntu, Debian and other apt-based distributions

```shell
$ sudo apt install libsodium-dev libgmp-dev pkg-config
```

#### Arch Linux

```shell
$ sudo pacman -Syu --needed libsodium gmp
```

### MacOS

[Homebrew](https://brew.sh/) needs to be installed.

```shell
$ brew install libsodium gmp pkg-config
```

#### M1 (ARM)

In case `libsodium` or `gmp` cannot find either include or lib paths, try explicitly set environment vars:

```shell
export CFLAGS="-I/opt/homebrew/Cellar/gmp/6.2.1_1/include/ -L/opt/homebrew/Cellar/gmp/6.2.1_1/lib/"
export DYLD_LIBRARY_PATH=/opt/homebrew/lib/
pip3 install --user pytezos
```

For running tests you might also need to export `LD_LIBRARY_PATH`:

```shell
export LD_LIBRARY_PATH=/opt/homebrew/lib/
```

### Windows

The recommended way is to use WSL and then follow the instructions for Linux,
but if you feel lucky you can try to install natively:

1. Install MinGW from [https://osdn.net/projects/mingw/](https://osdn.net/projects/mingw/)
2. Make sure `C:\MinGW\bin` is added to your `PATH`
3. Download the latest libsodium-X.Y.Z-msvc.zip from [https://download.libsodium.org/libsodium/releases/](https://download.libsodium.org/libsodium/releases/).
4. Extract the Win64/Release/v143/dynamic/libsodium.dll from the zip file
5. Copy libsodium.dll to C:\Windows\System32\libsodium.dll

### From PyPi

```shell
$ pip install wheel setuptools pkginfo cryptography
$ pip install pytezos
```

### [Google Colab](https://colab.research.google.com)

`````python
>>> !apt install libsodium-dev libgmp-dev
>>> !pip install pytezos
`````

### Docker container

Verified & minified images for CI/CD https://hub.docker.com/r/bakingbad/pytezos/tags

```shell
$ # 1. Use image from registry
$ docker pull bakingbad/pytezos
$ # or build it yourself
$ docker build . -t pytezos
$ # 2. Use included docker-compose.yml
$ docker-compose up -d notebook
```

### Building from sources

Requirements:

* Python 3.9 to 3.13
* libsodium, coincurve, gmp
* make

```shell
$ # prepare environment
$ make install
# # run full CI with tests
$ make all
```

## Quick start

Read [quick start guide](https://pytezos.org/quick_start.html)  
Learn how to [enable Jupyter with Michelson](./src/michelson_kernel/README.md)

## API reference

Check out a complete [API reference](https://pytezos.org/contents.html)

### Inline documentation

If you are working in Jupyter/Google Colab or any other interactive console, you can display documentation for a particular class/method:

```python
>>> from pytezos import pytezos
>>> pytezos
```

### Publications

* Pytezos 2.0 release with embedded docs and smart contract interaction engine  
https://medium.com/coinmonks/high-level-interface-for-michelson-contracts-and-not-only-7264db76d7ae

* Materials from TQuorum:Berlin workshop - building an app on top of PyTezos and ConseilPy  
https://medium.com/coinmonks/atomic-tips-berlin-workshop-materials-c5c8ee3f46aa

* Materials from the EETH hackathon - setting up a local development infrastructure, deploying and interacting with a contract  
https://medium.com/tezoscommons/preparing-for-the-tezos-hackathon-with-baking-bad-45f2d5fca519

* Introducing integration testing engine  
https://medium.com/tezoscommons/testing-michelson-contracts-with-pytezos-513718499e93

### Contact

* Telegram chat: [@baking_bad_chat](https://t.me/baking_bad_chat)
* Slack channel: [#baking-bad](https://tezos-dev.slack.com/archives/CV5NX7F2L)

## Credits

* The project was initially started by Arthur Breitman, now it's maintained by Baking Bad team.
* Baking Bad is supported by Tezos Foundation
* Michelson test set from the Tezos repo is used to ensure the interpreter workability
* Michelson structured documentation by Nomadic Labs is used for inline help
