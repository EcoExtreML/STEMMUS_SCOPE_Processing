# STEMMUS_SCOPE processing

This document illustrates how to run the model STEMMUS_SCOPE as a developer. 
The workflow is executed using python and MATLAB on a Unix-like system where a MATLAB license is available.
To run the STEMMUS_SCOPE, you need MATLAB version `>=2019`.

The python packages are listed in the
[`environment.yml`](https://github.com/EcoExtreML/processing/blob/main/environment.yml)
file. Follow the instructions below to create conda environment.

<details>
  <summary>Create conda environment </summary>

Run the commands below in a terminal:

```sh
# Download and install Conda
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-pypy3-Linux-x86_64.sh
bash Mambaforge-pypy3-Linux-x86_64.sh 
-b -p ~/mamba

# Update base environment
. ~/mamba/bin/activate
mamba update --name base mamba

# Clone this repository
git clone https://github.com/EcoExtreML/processing.git

# Create a conda environment called 'stemmus' with all required dependencies
cd processing
mamba env create

# The environment can be activated with
. ~/mamba/bin/activate stemmus

```
</details>


# Run model in a Jupyter notebook

**On Snellius:**

[Snellius](https://servicedesk.surfsara.nl/wiki/display/WIKI/Snellius) is the
Dutch National supercomputer hosted at SURF.

The notebook [run_model_in_notebook_dev.ipynb](./notebooks/run_model_in_notebook_dev.ipynb) shows how to run the model.
Use the script
[`run_jupyter_lab_snellius_dev.sh`](https://github.com/EcoExtreML/processing/blob/main/run_jupyter_lab_snellius_dev.sh)
to create a Jupyter lab server on Snellius for running the notebook
interactively.

# Run model in a MATLAB script

**On CRIB:**

[CRIB](https://crib.utwente.nl/) is the ITC Geospatial Computing Platform.

1. Log in CRIB with your username and password and select a proper compute unit.
2. Check `config_file_crib.txt` and change the paths if needed, specifically
   "InputPath" and "OutputPath".
3. click on the `Remote Desktop` in the
Launcher. Click on the `Applications`. You will find the 'MATLAB' software under
the `Research`. 
4. After clicking on 'MATLAB', it asks for your account information that is
connected to a MATLAB license.
5. Open the file `run_model_in_matlab_dev.m` and set the paths inside the script.
6. Then, run the main script `run_model_in_matlab_dev.m`.

# Recipe of model execution

The execution of the model includes following steps:

- Update/set config files
- Create input directories, prepare input files 
- Run the model
- Create output directories, prepare output files
- Create exe file
