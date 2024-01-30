# Basic Model Interface
The [Basic Model Interface](https://csdms.colorado.edu/wiki/BMI) is a standard way of communicating with models.
PyStemmusScope implements the Basic Model Interface for STEMMUS_SCOPE.

There are multiple ways to run the STEMMUS_SCOPE Basic Model Interface.
For the model, we generated Matlab Compiler Runtime executable file (only available for x86 Linux).
This requires installation of MCR.
The other option is to use the Dockerized version of the executable, available on ghcr.io/ecoextreml/stemmus_scope.

For more information on each method, see the sections below.

## Installation and setup

### Dockerized executable
STEMMUS_SCOPE has a Docker image available. This allows you to run the executable file without having to install MCR.
The Docker image is available at https://ghcr.io/ecoextreml/stemmus_scope. The Docker image is created using the docker file [here](https://github.com/EcoExtreML/STEMMUS_SCOPE/blob/main/Dockerfile).

To use the Docker image, use the `DockerImage` setting in the configuration file:
```sh
WorkDir=/home/username/tmp/stemmus_scope
...
DockerImage=ghcr.io/ecoextreml/stemmus_scope:1.5.0
```

It is best to add the version tag here too (`:1.5.0`), this way the BMI will warn you if the version might be incompatible.

Note that the `docker` package for python is required here. Install this with `pip install PyStemmusScope[docker]`.
Additionally, [Docker](https://docs.docker.com/get-docker/) itself has to be installed.

### Local executable file
The executable file can be downloaded from the STEMMUS_SCOPE repository. More specifically [here](https://github.com/EcoExtreML/STEMMUS_SCOPE/tree/main/run_model_on_snellius/exe).

To be able to run this executable, you need a Linux x86 system, along with Matlab Compiler Runtime R2023a. MCR is available [here](https://nl.mathworks.com/products/compiler/matlab-runtime.html).

To use the local executable file, add the path to the executable file to the config file. E.g.:
```
WorkDir=/home/username/tmp/stemmus_scope
...
ExeFilePath=/path/to/executable/STEMMUS_SCOPE
```

Alternatively, if the environmental variable `STEMMUS_SCOPE` is configured, the BMI will use this if the ExeFilePath or DockerImage are not set in the configuration file.

## Using the BMI

A [notebook demonstration the use of the Basic Model Interface](notebooks/BMI_demo.ipynb) is available.
For more information on using BMI, see the [CSDMS website](https://csdms.colorado.edu/wiki/BMI).

If you need access to other model variables that are not yet available in the BMI, please raise an issue on the [STEMMUS_SCOPE repository](https://github.com/EcoExtreML/STEMMUS_SCOPE/issues), or leave a comment if an issue is open already.

## grpc4bmi

A [Docker image is available](https://ghcr.io/ecoextreml/stemmus_scope-grpc4bmi) in which the model as well as the Python BMI have been wrapped in a container. The Docker image is created using the Docker file [here](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/Dockerfile) and allows communication with a STEMMUS_SCOPE BMI through [grpc4bmi](https://grpc4bmi.readthedocs.io/en/latest/).

Doing so avoids the needs to install PyStemmusScope yourself, only Docker/apptainer and a python environment with grpc4bmi are required. Please note you should not specify `DockerImage` or `ExeFilePath` in the config file if you are using the grpc4bmi interface. 

A demonstration is available [here](notebooks/grpc4bmi_demo.ipynb)

## Developer instructions

The Python BMI implemented in this package communicates with the Matlab code through STDIN/STDOUT, or via a socket to the Docker container.
Over this interface, three commands can be sent to Matlab:

1. `initialize "path_to_cfg_file.txt"`
2. `update`
3. `finalize`

After the initialize and update steps, the Matlab process writes the state of any BMI exposed variables to an hdf5-file in the directory of `OutputPath` as defined in the configuration file.

The Python BMI interfaces with this file to allow the variables to be read and set.

### Adding/changing exposed variables

Step one of changing the exposed variables is to change the Matlab code and generating a new MCR executable (and possibly Docker image).
The exposed variables are defined in [`STEMMUS_SCOPE/src/STEMMUS_SCOPE_exe.m`](https://github.com/EcoExtreML/STEMMUS_SCOPE/blob/main/src/STEMMUS_SCOPE_exe.m).
Under the `bmiVarNames` variable.
Make sure that you add the model variable here, as well as any info on the variable's grid.

The available variable names (`MODEL_INPUT_VARNAMES`, `MODEL_OUTPUT_VARNAMES`), their units (`VARNAME_UNITS`), datatypes (`VARNAME_DTYPE`) and grids (`VARNAME_GRID`) are defined in constants at the top of the file `PyStemmusScope/bmi/implementation.py`.
These have to be updated to reflect the changes in the state file.

Lastly you have to update the `get_variable` and `set_variable` functions in `PyStemmusScope/bmi/implementation.py`.
Here you define how the python code can access them.
While writing the code you can inspect the state using `model.state`, which allows you to view the full contents of the HDF5 file for easier debugging.

After implementing the BMI changes, a new [STEMMUS_SCOPE Docker image](https://github.com/EcoExtreML/STEMMUS_SCOPE/pkgs/container/stemmus_scope) should be released that is compatible with the new BMI implementation. A new release usually includes a new tag. Then, you need to update the `compatible_tags` variable of the class `StemmusScopeDocker` in `PyStemmusScope/bmi/docker_process.py`.
