# processing

This repositary includes python modules for running the STEMMUS-SCOPE model in a
notebook. 

The workflow is executed using python and MATLAB Runtime on a Unix-like system.
The python packages are listed in the
[`environment.yml`](https://github.com/EcoExtreML/processing/blob/main/environment.yml)
file. Follow the instructions below to create conda environment and install
MATLAB Runtime.

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

<details>
  <summary>Install MATLAB Runtime </summary>

To run the STEMMUS_SCOPE, you need MATLAB Runtime version `2021a`. Use this
[download link](https://nl.mathworks.com/products/compiler/matlab-runtime.html)
and follow [this
instruction](https://nl.mathworks.com/help/compiler/install-the-matlab-runtime.html)
to install it.  

**On Snellius:**

[Snellius](https://servicedesk.surfsara.nl/wiki/display/WIKI/Snellius) is the
Dutch National supercomputer hosted at SURF. MATLAB Runtime is installed on
Snellius, see the script
[`run_jupyter_lab_on_compute_node.sh`](https://github.com/EcoExtreML/processing/blob/main/run_jupyter_lab_on_compute_node.sh)
on how to load the module.
</details>

# Run jupyter notebook

Open a terminal and run:

```sh
jupyter lab
```

JupyterLab will open automatically in your browser.

**On Snellius:**

Use the script
[`run_jupyter_lab_on_compute_node.sh`](https://github.com/EcoExtreML/processing/blob/main/run_jupyter_lab_on_compute_node.sh)
to create a jupyter lab server on Snellius for running the notebook
interactively.

# Run jupyter notebook on CRIB

[CRIB](https://crib.utwente.nl/) is the ITC Geospatial Computing Platform.
Currently, running the notebook on CRIB is not supported because MATLAB Runtime
can not be installed there.

# Recipe of model execution

The execution of the model includes following steps:

- Create exe file
- Update/set config files
- Create input directories, prepare input files 
- Run the model
- Create output directories, prepare output files
