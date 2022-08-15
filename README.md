
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

This repository includes the python package `PyStemmusScope` for running the STEMMUS-SCOPE model.
<!-- markdown-link-check-disable-next-line -->
The model source code is in MATLAB and available in the [STEMMUS_SCOPE repository](https://github.com/EcoExtreML/STEMMUS_SCOPE).

See the relevant instructions for `Users` or `Developers` on how to run the model.

## Users

As a user, you don't need to have a MATLAB license to run the STEMMUS-SCOPE model. The workflow is executed using python and MATLAB Runtime on a Unix-like system.

### Installations 

Follow the instructions below to install `PyStemmusScope` and MATLAB Runtime.

<details>
  <summary>Install PyStemmusScope in a conda environment</summary>

PyStemmusScope is installed in a conda environment, see the the
[`environment.yml`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/environment.yml)
file.

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

<details>
  <summary>Install MATLAB Runtime </summary>

To run the STEMMUS_SCOPE, you need MATLAB Runtime version `2021a`.

In a terminal:

```sh
# Download MATLAB Runtime for Linux
wget https://ssd.mathworks.com/supportfiles/downloads/R2021a/Release/6/deployment_files/installer/complete/glnxa64/MATLAB_Runtime_R2021a_Update_6_glnxa64.zip

# Unzip the file
unzip MATLAB_Runtime_R2021a_Update_6_glnxa64.zip

# Install it
cd MATLAB_Runtime_R2021a_Update_6_glnxa64
sudo -H ./install -mode silent -agreeToLicense yes
```

For more information on how to download and install it, see the links below:
- [download](https://nl.mathworks.com/products/compiler/matlab-runtime.html)
- [intallation](https://nl.mathworks.com/help/compiler/install-the-matlab-runtime.html)

</details>

Open a terminal, make sure the environment is activated. Then, run `jupyter lab`:

```sh
jupyter lab
```

JupyterLab will open automatically in your browser. Now, you can run the notebook [run_model_in_notebook.ipynb](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/notebooks/run_model_in_notebook.ipynb).

### On Snellius

[Snellius](https://servicedesk.surfsara.nl/wiki/display/WIKI/Snellius) is the
Dutch National supercomputer hosted at SURF. MATLAB Runtime is installed on
Snellius, see the script
[`run_jupyter_lab_snellius.sh`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/run_jupyter_lab_snellius.sh)
on how to load the module. Also, use the script
[`run_jupyter_lab_snellius.sh`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/run_jupyter_lab_snellius.sh)
to create a jupyter lab server on Snellius for running the notebook
[run_model_in_notebook.ipynb](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/notebooks/run_model_in_notebook.ipynb)
interactively.

### On CRIB

[CRIB](https://crib.utwente.nl/) is the ITC Geospatial Computing Platform.
Currently, running the model exceutable file and therefore the notebook
[run_model_in_notebook.ipynb](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/notebooks/run_model_in_notebook.ipynb)
on CRIB is not supported because MATLAB Runtime can not be installed there.

## Developers

If you want to contribute to the development of PyStemmusScope,
have a look at the [contribution guidelines](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/CONTRIBUTING.md).

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).
