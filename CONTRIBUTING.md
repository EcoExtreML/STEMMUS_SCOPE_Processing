# Contributing Guide

This repository includes the python package `PyStemmusScope` for running the STEMMUS-SCOPE model.

## Configure the python package for development and testing

To contribute to the development of the python package, we recommend installing
the package in development mode.


### Installation

First, clone this repository:

```sh
git clone https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing.git
```

Then install the package (On Windows, use `python` instead of `python3`):

```sh
cd STEMMUS_SCOPE_Processing
python3 -m install -e .[dev]
```

### Run tests

The testing framework used here is [PyTest](https://pytest.org). You can run
tests as (On Windows, use `python` instead of `python3`):

```sh
python3 -m pytest
```

### Build documentation

To build the documentation locally:

```sh
cd docs/
make html
```

Then open `_build/html/index.html` in a web broser to preview the documentation.

### Run formatting tools

You can use `prospector` to get information about errors, potential problems and convention violations. To run:

```sh
prospector
```

To format the import statements, you can use `isort` as:

```sh
isort
```

## Development of STEMMUS_SCOPE model

<!-- markdown-link-check-disable-next-line -->
To contribute to the STEMMUS_SCOPE model, you need access to the model source code that is stored in the repository [STEMMUS_SCOPE](https://github.com/EcoExtreML/STEMMUS_SCOPE).
