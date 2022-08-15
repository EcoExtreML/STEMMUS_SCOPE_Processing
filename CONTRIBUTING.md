# Contributing Guide

This repository includes the python package `PyStemmusScope` for running the STEMMUS-SCOPE model.

## Configure the python package for development and testing

To contribute to development of the python package, we recommend installing the package in development mode. 


### Installation 

First, clone this repository:

```sh
git clone https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing.git
```

Then install the package:

```sh
cd STEMMUS_SCOPE_Processing
pip install -e .
```

or

```sh
python setup.py develop
```

### Run tests

The testing framework used here is [PyTest](https://pytest.org). You can run
tests as:

```sh
pytest
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
To contribuute to STEMMUS_SCOPE model, you need access to model source code that is stored in the repository [STEMMUS_SCOPE](https://github.com/EcoExtreML/STEMMUS_SCOPE). You also need a MATLAB license.

### Development on Snellius using MATLAB

[Snellius](https://servicedesk.surfsara.nl/wiki/display/WIKI/Snellius) is the
Dutch National supercomputer hosted at SURF. To run the STEMMUS_SCOPE, you need MATLAB version `>=2019`. MATLAB is installed on
Snellius, see the script
[`run_jupyter_lab_snellius_dev.sh`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/run_jupyter_lab_snellius_dev.sh)
on how to load the module.

The script
[`run_jupyter_lab_snellius_dev.sh`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/run_jupyter_lab_snellius_dev.sh)
also creates a jupyter lab server on Snellius for running the notebook
interactively. Make sure that you create the `pystemmusscope` conda environment, see [User guide](https://pystemmusscope.readthedocs.io/en/latest/readme_link.html#installations).

### Development on CRIB using MATLAB

[CRIB](https://crib.utwente.nl/) is the ITC Geospatial Computing Platform.

1. Log in CRIB with your username and password and select a proper compute unit.
2. Check `config_file_crib.txt` and change the paths if needed, specifically
   "InputPath" and "OutputPath".
3. click on the `Remote Desktop` in the
Launcher. Click on the `Applications`. You will find the 'MATLAB' software under
the `Research`.
4. After clicking on 'MATLAB', it asks for your account information that is
connected to a MATLAB license.
5. Open the file `STEMMUS_SCOPE_run.m` and set the paths inside the script and setup the model.
6. Then, run the main script `STEMMUS_SCOPE_run.m`.
