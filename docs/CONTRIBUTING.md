# Contributing Guide

If you want to contribute to `PyStemmusScope`, we recommend installing
the package in editable mode. The instructions below will guide you though the steps
required.

### Dependencies

Check the package `dependencies` and `optional dependencies` in the
`pyproject.toml` file in the root directory of the repository. The package
dependecies are those packages that are required to build the package as a
software. The optional dependencies are those packages that are required to run
the tests, build the documentation, and format the code.

### Installation in editable mode

First, clone this repository:

```sh
git clone https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing.git
```

Then install the package (On Windows, use `python` instead of `python3`):

```sh
cd STEMMUS_SCOPE_Processing
python3 -m install -e .[dev]
```

### Running tests

The testing framework used here is [PyTest](https://pytest.org). You can run
tests as (On Windows, use `python` instead of `python3`):

```sh
python3 -m pytest
```

### Building the documentation

To install the documentation dependencies (On Windows, use `python` instead of `python3`):

```sh
cd STEMMUS_SCOPE_Processing
python3 -m install -e .[docs]
```

To edit the documentation locally, do:

```sh
mkdocs serve
```

Then open the local hyperlink displayed in the terminal, e.g.:
```
INFO     -  [13:23:44] Serving on http://127.0.0.1:8000/
```

### Run formatting tools

Formatting configs are listed in the `pyproject.toml` file. You can use `ruff`
to get information about errors, potential problems and convention violations.
To run:

```sh
ruff check .
```

It is possible to fix some of the errors automatically. To do so, run:

```sh
ruff check --fix .
```

To format the import statements, you can use `isort` as:

```sh
isort
```

### BMI Developer instructions

The Python BMI implemented in this package communicates with the Matlab code
through STDIN/STDOUT, or via a socket to the Docker container.
Over this interface, three commands can be sent to Matlab:

1. `initialize "path_to_cfg_file.txt"`
2. `update`
3. `finalize`

After the initialize and update steps, the Matlab process writes the state of
any BMI exposed variables to an hdf5-file in the directory of `OutputPath` as
defined in the configuration file.

The Python BMI interfaces with this file to allow the variables to be read and set.

#### Adding/changing exposed variables

Step one of changing the exposed variables is to change the Matlab code and
generating a new MCR executable (and possibly Docker image). The exposed
variables are defined in
[`STEMMUS_SCOPE/src/STEMMUS_SCOPE_exe.m`](https://github.com/EcoExtreML/STEMMUS_SCOPE/blob/main/src/STEMMUS_SCOPE_exe.m).
Under the `bmiVarNames` variable. Make sure that you add the model variable
here, as well as any info on the variable's grid.

The available variable names (`MODEL_INPUT_VARNAMES`, `MODEL_OUTPUT_VARNAMES`),
their units (`VARNAME_UNITS`), datatypes (`VARNAME_DTYPE`) and grids
(`VARNAME_GRID`) are defined in constants at the top of the file
`PyStemmusScope/bmi/implementation.py`. These have to be updated to reflect the
changes in the state file.

Lastly you have to update the `get_variable` and `set_variable` functions in
`PyStemmusScope/bmi/implementation.py`. Here you define how the python code can
access them. While writing the code you can inspect the state using
`model.state`, which allows you to view the full contents of the HDF5 file for
easier debugging.

After implementing the BMI changes, a new [STEMMUS_SCOPE Docker
image](https://github.com/EcoExtreML/STEMMUS_SCOPE/pkgs/container/stemmus_scope)
should be released that is compatible with the new BMI implementation. A new
release usually includes a new tag. Then, you need to update the
`compatible_tags` variable of the class `StemmusScopeDocker` in
`PyStemmusScope/bmi/docker_process.py`.


## Making a release

This section describes how to make a release in 3 parts:

1. preparation
1. making a release on GitHub

### (1/2) Preparation

1. Update the <CHANGELOG.md> (don't forget to update links at bottom of page)
2. Verify that the information in `CITATION.cff` is correct, and that `.zenodo.json` contains equivalent data
3. Make sure the version has been updated.
4. Run the unit tests with `pytest -v`

### (2/2) GitHub

Don't forget to also make a [release on
GitHub](https://github.com/EcoExtreML/stemmus_scope_processing/releases/new).
This will trigger the github action `python-publish.yml` that publishes the
package on PyPI. If your repository uses the GitHub-Zenodo integration this will
also trigger Zenodo into making a snapshot of your repository and sticking a DOI
on it.
