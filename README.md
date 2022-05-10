# processing
Example notebooks showing how to launch the STEMMUS-SCOPE model.

The whole workflow is executed using python and all the required packages are listed in the [`environment.yml`](https://github.com/EcoExtreML/processing/blob/main/environment.yml) file. Please use [`environment.yml`](https://github.com/EcoExtreML/processing/blob/main/environment.yml) to configure your conda environment. For more details about how to setup your conda environment, check [here](https://github.com/EcoExtreML/STEMMUS_SCOPE/tree/main/utils/csv_to_nc) (see steps 1 and 2).

Use the script [`run_jupyter_lab_on_compute_node.sh`](https://github.com/EcoExtreML/processing/blob/main/run_jupyter_lab_on_compute_node.sh) to create a jupyter lab server on Snellius for running the notebook interactively.

# Recipe of model execution
The execution of the model includes following steps:

- Create exe file
- Update/set config files
- Create input directories, prepare input files 
- Run the model
- Create output directories, prepare output files
