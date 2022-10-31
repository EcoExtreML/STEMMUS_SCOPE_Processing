
<!-- (Customize these badges with your own links, and check https://shields.io/ or https://badgen.net/ to see which other badges are available.) -->


[![github repo badge](https://img.shields.io/badge/github-repo-000.svg?logo=github&labelColor=gray&color=blue)](https://github.com/EcoExtreML/stemmus_scope_processing)
[![build](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/build.yml/badge.svg)](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/build.yml)
[![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![sonarcloud](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/sonarcloud.yml/badge.svg)](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/sonarcloud.yml)
[![github license badge](https://img.shields.io/github/license/EcoExtreML/stemmus_scope_processing)](https://github.com/EcoExtreML/stemmus_scope_processing)
[![Documentation Status](https://readthedocs.org/projects/pystemmusscope/badge/?version=latest)](https://pystemmusscope.readthedocs.io/en/latest/?badge=latest)

<!-- [![RSD](https://img.shields.io/badge/rsd-pystemmusscope-00a3e3.svg)](https://www.research-software.nl/software/pystemmusscope)
[![workflow pypi badge](https://img.shields.io/pypi/v/pystemmusscope.svg?colorB=blue)](https://pypi.python.org/project/pystemmusscope/)
[![DOI](https://zenodo.org/badge/DOI/<replace-with-created-DOI>.svg)](https://doi.org/<replace-with-created-DOI>)
[![workflow cii badge](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>/badge)](https://bestpractices.coreinfrastructure.org/projects/<replace-with-created-project-identifier>)
[![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=EcoExtreML_stemmus_scope_processing&metric=coverage)](https://sonarcloud.io/dashboard?id=EcoExtreML_stemmus_scope_processing)
[![cffconvert](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/cffconvert.yml)
[![markdown-link-check](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/markdown-link-check.yml/badge.svg)](https://github.com/EcoExtreML/stemmus_scope_processing/actions/workflows/markdown-link-check.yml) -->

This repository includes the python package `PyStemmusScope` for running the
STEMMUS-SCOPE model. 
<!-- markdown-link-check-disable-next-line -->
The model source code, executable file and utility files are available in the
[STEMMUS_SCOPE repository](https://github.com/EcoExtreML/STEMMUS_SCOPE). The
input datasets are available on Snellius and CRIB.
First, make sure you have right access to the repository and data. Then, see the
notebook
[run_model_in_notebook.ipynb](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/notebooks/run_model_in_notebook.ipynb)
which provides different options to run the model, see [Run the model](#run-the-model).

## Run the model

1. Using executable file: As a user, you don't need to have a MATLAB license to
run the STEMMUS-SCOPE model. If `PyStemmusScope` and `MATLAB Runtime` are
installed on a Unix-like system (e.g. your own machine, Snellius or WSL), you
can run STEMMUS_SCOPE using the executable file.
2. Using Matlab: If `PyStemmusScope` and `Matlab` are installed, you can run
STEMMUS_SCOPE from the source code, for example on Snellius or CRIB.
3. Using Octave: If `PyStemmusScope` and latest `Octave` including required
packages are installed, you can run STEMMUS_SCOPE from its source code, for
example on CRIB or your own machine.

See section [Installations](#installations) for required packages.

## Installations

### On Snellius

[Snellius](https://servicedesk.surfsara.nl/wiki/display/WIKI/Snellius) is the
Dutch National supercomputer hosted at SURF. MATLAB and MATLAB Runtime are
installed on Snellius, see the script
[`run_jupyter_lab_snellius.sh`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/run_jupyter_lab_snellius.sh)
on how to load the module. Also, use the same script to create a jupyter lab
server for running notebooks interactively. The script activates the conda
environment `pystemmusscope`. Make sure that you create the `pystemmusscope`
conda environment before submitting the the bash script. See
[Create pystemmusscope conda environment](#create-pystemmusscope-conda-environment).

### On CRIB

[CRIB](https://crib.utwente.nl/) is the ITC Geospatial Computing Platform. You
can run the model using `Matlab` or `Octave`. Currently, running the 
exceutable file on CRIB is not supported because MATLAB Runtime can not be
installed there. See [Install PyStemmusScope](#install-pystemmusscope).

### On your own machine

Choose how do you want to run the model, see [Run the model](#run-the-model).

### Install PyStemmusScope

Run the commands below in a terminal:

```sh
# will be replaced by `pip install pystemmusscope`
python3 -m pip install git+https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing.git@main
```

or

Open a jupyter notebook and run the code below in a cell:

```python
!pip install git+https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing.git@main
```

### Install jupyterlab

Jupyterlab is needed to run notebooks. Run the commands below in a terminal:

```sh
python3 -m pip install jupyterlab

```

Open a terminal, make sure the environment is activated. Then, run `jupyter lab`:

```sh
jupyter lab
```

JupyterLab will open automatically in your browser. Now, you can run the
notebook
[run_model_in_notebook.ipynb](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/notebooks/run_model_in_notebook.ipynb).

### Install MATLAB Runtime

To run the STEMMUS_SCOPE, you need MATLAB Runtime version `2021a` and a Unix-like system.

In a terminal:

```sh
# Download MATLAB Runtime for Linux
wget https://ssd.mathworks.com/supportfiles/downloads/R2021a/Release/6/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2021a_Update_6_glnxa64.zip

# Unzip the file
unzip MATLAB_Runtime_R2021a_Update_6_glnxa64.zip -d MATLAB_Runtime

# Install it
cd MATLAB_Runtime
sudo -H ./install -mode silent -agreeToLicense yes
```

For more information on how to download and install MATLAB Runtime, see the links below:
  - [download](https://nl.mathworks.com/products/compiler/matlab-runtime.html)
  - [installation](https://nl.mathworks.com/help/compiler/install-the-matlab-runtime.html)

### Install WSL

As the STEMMUS-SCOPE executable only supports Unix-like systems, Windows users
cannot run STEMMUS-SCOPE natively. However, users of Windows 10 and newer can
use WSL ([Windows Subsystem for
Linux](https://docs.microsoft.com/en-us/windows/wsl/)) to run the model.
Check the <a
href="https://docs.microsoft.com/en-us/windows/wsl/install">Microsoft Guide</a>
for a compatibility information and for general WSL instructions.
If no installation exists, a Ubuntu distribution can be installed using the following commands:
```sh
wsl --install
```

After installation, you can start up the WSL instance and update the default software:

```sh
sudo apt update && sudo apt upgrade
```

You can now set up a python environment using either python's `venv`, or use Conda/Mamba.
Note that the command to run python and pip can be `python3` and `pip3` by default.

For the rest of the installation instructions simply follow the steps below.
Note that it is possible to access files from the Windows filesystem from within
WSL, by accessing, e.g., `/mnt/c/` instead of `C:\`. This means that large input
data files can be stored on your Windows installation instead of inside the WSL
distro. However, WSL does not have write permission. Therefore, output data will
be stored within WSL. Make sure that `WorkDir` in the model config file is set
correctly.

### Create pystemmusscope conda environment

If a conda environment is neeed, run the commands below in a terminal:

```sh
# Download and install Mamba on linux
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-pypy3-Linux-x86_64.sh
bash Mambaforge-pypy3-Linux-x86_64.sh -b -p ~/mamba

# Update base environment
. ~/mamba/bin/activate
mamba update --name base mamba

# Download environment file
wget https://raw.githubusercontent.com/EcoExtreML/STEMMUS_SCOPE_Processing/main/environment.yml

# Create a conda environment called 'pystemmusscope' with all required dependencies
mamba env create -f environment.yml

# The environment can be activated with
. ~/mamba/bin/activate pystemmusscope

```
