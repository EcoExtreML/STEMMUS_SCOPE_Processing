# Basic Model Interface
The [Basic Model Interface](https://csdms.colorado.edu/wiki/BMI) is a standard way of communicating with models.
PyStemmusScope implements the Basic Model Interface for STEMMUS_SCOPE.

There are multiple ways to run the STEMMUS_SCOPE Basic Model Interface.
The first is using a local Matlab Compiler Runtime executable file (only available for x86 Linux).
This requires installation of MCR.
The other option is to use the Dockerized version of the executable, available on ghcr.io/ecoextreml/stemmus_scope.

For more information on each method, see the sections below.

## Local executable file
The executable file can be downloaded from the STEMMUS_SCOPE repository. More specifically [here](https://github.com/EcoExtreML/STEMMUS_SCOPE/tree/main/run_model_on_snellius/exe).

To be able to run this executable, you need a Linux x86 system, along with Matlab Compiler Runtime R2023a. MCR is available [here](https://nl.mathworks.com/products/compiler/matlab-runtime.html).

To use the local executable file, add the path to the executable file to the config file. E.g.:
```
WorkDir=/home/username/tmp/stemmus_scope
...
ExeFilePath=/path/to/executable/STEMMUS_SCOPE
```

Alternatively, if the environmental variable `STEMMUS_SCOPE` is configured, the BMI will use this if the ExeFilePath or DockerImage are not set in the configuration file.

## Dockerized executable
STEMMUS_SCOPE also has a Docker image available. This allows you to run the executable file without having to install MCR.
The Docker image is available at https://ghcr.io/ecoextreml/stemmus_scope

To use the Docker image, use the `DockerImage` setting in the configuration file:
```sh
WorkDir=/home/username/tmp/stemmus_scope
...
DockerImage=ghcr.io/ecoextreml/stemmus_scope:1.5.0
```

It is best to add the version tag here too (`:1.5.0`), this way the BMI will warn you if the version might be incompatible.

Note that the `docker` package for python is required here. Install this with `pip install PyStemmusScope[docker]`.
Additionally, [Docker](https://docs.docker.com/get-docker/) itself has to be installed.
