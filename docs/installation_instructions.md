# Installation instructions

This is the installation instruction for the python package `PyStemmusScope`,
which allows for preparing data and running the STEMMUS-SCOPE model. The model
source code [STEMMUS_SCOPE
repository](https://github.com/EcoExtreML/STEMMUS_SCOPE). For model-specific
instructions, check the `Getting started` page.

Note that the latest version of `PyStemmusScope` is compatible with latest
version of `STEMMUS-SCOPE` model.

## Install PyStemmusScope

To install the package, you need to have Python ">=3.9, <3.12" installed.
Run the commands below in a terminal (On Windows, use `python` instead of
`python3`):

```sh
python3 -m pip install pystemmusscope
```

or

Open a jupyter notebook and run the code below in a cell:

```python
!pip install pystemmusscope
```

On CRIB, you can use the following command to install the package:

```sh
python3 -m pip install --user pystemmusscope
```

## Install jupyterlab

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
[run_model_on_different_infra.ipynb](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/docs/notebooks/run_model_on_different_infra.ipynb).

## Install WSL [optional]

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

## Create pystemmusscope conda environment [optional]

If a conda environment is needed, for example, on Snellius, run the commands
below in a terminal:

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
