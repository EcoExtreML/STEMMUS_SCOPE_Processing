# Installation instructions
The installation instructions depend on which computers you want to run the model, be it
Snellius, CRIB, or your own local machine.

## On Snellius

[Snellius](https://servicedesk.surfsara.nl/wiki/display/WIKI/Snellius) is the
Dutch National supercomputer hosted at SURF. MATLAB and MATLAB Runtime are
installed on Snellius, see the script
[`run_jupyter_lab_snellius.sh`](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/run_jupyter_lab_snellius.sh)
on how to load the module. Also, use the same script to create a jupyter lab
server for running notebooks interactively. The script activates the conda
environment `pystemmusscope`. Make sure that you create the `pystemmusscope`
conda environment before submitting the the bash script. See
[Create pystemmusscope conda environment](#create-pystemmusscope-conda-environment).

## On CRIB

[CRIB](https://crib.utwente.nl/) is the ITC Geospatial Computing Platform. You
can run the model using `Matlab` or `Octave`. Currently, running the
exceutable file on CRIB is not supported because MATLAB Runtime can not be
installed there. See [Install PyStemmusScope](#install-pystemmusscope).

## On your own machine

Choose how do you want to run the model, see [Run the model](notebooks/run_model_on_different_infra.ipynb).

## Install PyStemmusScope

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

## Install MATLAB Runtime

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

## Install WSL

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

## Create pystemmusscope conda environment

If a conda environment is needed, run the commands below in a terminal:

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
