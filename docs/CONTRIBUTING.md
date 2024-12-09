# Contributing Guide

We welcome any kind of contributions to our software, from simple
comment or question to a full fledged [pull
request](https://help.github.com/articles/about-pull-requests/). Please
read and follow our [Code of Conduct](./CODE_OF_CONDUCT.md).

A contribution can be one of the following cases:

1. you have a question;
2. you think you may have found a bug (including unexpected behavior);
3. you want to make some kind of change to the code base (e.g. to fix a
    bug, to add a new feature, to update documentation).
4. you want to make a release

The sections below outline the steps in each case.

## You have a question

1. use the search functionality
    [here](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/issues) to see if
    someone already filed the same issue;
2. if your issue search did not yield any relevant results, make a new issue;
3. apply the \"Question\" label; apply other labels when relevant.

## You think you may have found a bug

1. use the search functionality
    [here](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/issues) to see
    if someone already filed the same issue;
2. if your issue search did not yield any relevant results, make a new issue,
    making sure to provide enough information to the rest of the community to
    understand the cause and context of the problem. Depending on the issue, you
    may want to include: - the [SHA
    hashcode](https://help.github.com/articles/autolinked-references-and-urls/#commit-shas)
    of the commit that is causing your problem; - some identifying information
    (name and version number) for dependencies you\'re using; - information
    about the operating system;
3. apply relevant labels to the newly created issue.

## You want to make some kind of change to the code base

1. (**important**) announce your plan to the rest of the community
    *before you start working*. This announcement should be in the form
    of a (new) issue;
2. (**important**) wait until some kind of consensus is reached about
    your idea being a good idea;
3. if needed, fork the repository to your own Github profile and create your own
    feature branch off of the latest main commit. While working on your feature
    branch, make sure to stay up to date with the main branch by pulling in
    changes, possibly from the \'upstream\' repository (follow the instructions
    [here](https://help.github.com/articles/configuring-a-remote-for-a-fork/)
    and [here](https://help.github.com/articles/syncing-a-fork/));
4. If you are using [Visual Studio Code](https://code.visualstudio.com), some
   extensions will be recommended and you are offered to run inside a
   [DevContainer](https://containers.dev) in which the dependencies are already
   installed;

In case you feel like you\'ve made a valuable contribution, but you
don\'t know how to write or run tests for it, or how to generate the
documentation: don\'t let this discourage you from making the pull
request; we can help you! Just go ahead and submit the pull request, but
keep in mind that you might be asked to append additional commits to
your pull request.

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
