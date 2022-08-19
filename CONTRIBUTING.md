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
To contribute to the STEMMUS_SCOPE model, you need access to the model source code that is stored in the repository [STEMMUS_SCOPE](https://github.com/EcoExtreML/STEMMUS_SCOPE). You also need a MATLAB license.

### Development on Snellius using MATLAB

[Snellius](https://servicedesk.surfsara.nl/wiki/display/WIKI/Snellius) is the
Dutch National supercomputer hosted at SURF. MATLAB `2021a` is installed on
Snellius, see the script
[`run_jupyter_lab_snellius_dev.sh`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/run_jupyter_lab_snellius_dev.sh)
on how to load the module.

The script `run_jupyter_lab_snellius_dev.sh` activates the conda environment `pystemmusscope` and creates a jupyter lab server on Snellius for running the notebook
interactively. Make sure that you create the `pystemmusscope` conda environment before submitting the the bash script. See **Create pystemmusscope environment** below.

<details>
  <summary>Create pystemmusscope environment</summary>

Run the commands below in a terminal:

```sh
# Download and install Mamba on linux
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-pypy3-Linux-x86_64.sh
bash Mambaforge-pypy3-Linux-x86_64.sh -b -p ~/mamba

# Update base environment
. ~/mamba/bin/activate
mamba update --name base mamba

# Download environment file
wget https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/environment.yml

# Create a conda environment called 'pystemmusscope' with all required dependencies
mamba env create -f environment.yml

# The environment can be activated with
. ~/mamba/bin/activate pystemmusscope

```
</details>


### Development on CRIB using MATLAB

[CRIB](https://crib.utwente.nl/) is the ITC Geospatial Computing Platform.

MATLAB `2021a` is installed on CRIB that is compatiable with Python `3.8`, see [Versions of Python Compatible with MATLAB Products](https://www.mathworks.com/content/dam/mathworks/mathworks-dot-com/support/sysreq/files/python-compatibility.pdf).

1. Log in CRIB with your username and password and select a proper compute unit.
2. Install `PyStemmusScope` package. This step needs to be done once.
  <details>
    <summary>Install pystemmusscope with python 3.8</summary>

  Run the commands below in a terminal:

  ```sh
  # Download and install Mamba on linux
  wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-pypy3-Linux-x86_64.sh
  bash Mambaforge-pypy3-Linux-x86_64.sh -b -p ~/mamba

  # Update base environment
  . ~/mamba/bin/activate
  mamba update --name base mamba

  # Download environment file
  wget https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/environment_3.8.yml

  # Create a conda environment called 'pystemmusscope' with all required dependencies
  mamba env create -f environment_3.8.yml
  ```
  </details>

3. click on the `Remote Desktop` in the
Launcher. Click on the `Applications`. You will find the 'MATLAB' software under
the `Research`.
4. After clicking on 'MATLAB', it asks for your account information that is
connected to a MATLAB license.
5. Open the file `STEMMUS_SCOPE_run.m` and set the path of `config_file` to `../config_file_crib.txt` and change `WorkDir` and other configurations in `model.setup()`.
6. Then, run the main script `STEMMUS_SCOPE_run.m`.
