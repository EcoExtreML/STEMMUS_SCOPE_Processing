# Basic Model Interface

The [Basic Model Interface](https://csdms.colorado.edu/wiki/BMI) is a standard
way of communicating with models. PyStemmusScope implements the Basic Model
Interface for STEMMUS_SCOPE. There are multiple ways to run the STEMMUS_SCOPE
Basic Model Interface. For the model, we generated Matlab Compiler Runtime
executable file (only available for x86 Linux). This requires installation of
MCR. The other option is to use the Dockerized version of the executable,
available on
[https://ghcr.io/ecoextreml/stemmus_scope](https://ghcr.io/ecoextreml/stemmus_scope). For more
information on each method, see the sections below.

## Installation and setup

### Dockerized executable

STEMMUS_SCOPE has a Docker image available. This allows you to run the
executable file without having to install MCR. The Docker image is available at
[https://ghcr.io/ecoextreml/stemmus_scope](https://ghcr.io/ecoextreml/stemmus_scope).
The Docker image is created using the docker file
[here](https://github.com/EcoExtreML/STEMMUS_SCOPE/blob/main/Dockerfile). To use
the Docker image, use the `DockerImage` setting in the configuration file:

```sh
WorkDir=/home/username/tmp/stemmus_scope
...
DockerImage=ghcr.io/ecoextreml/stemmus_scope:1.6.2
```

It is best to add the version tag here too (`:1.6.2`), this way the BMI will
warn you if the version might be incompatible. Note that the `docker` package
for python is required. Install this with `pip install PyStemmusScope[docker]`.
Additionally, [Docker](https://docs.docker.com/get-docker/) itself has to be
installed.

### Local executable file

You can run the model using the executable file. It can be downloaded from the
STEMMUS_SCOPE repository,
[here](https://github.com/EcoExtreML/STEMMUS_SCOPE/tree/main/run_model_on_snellius/exe).
To be able to run this executable, you need a Linux x86 system, along with
Matlab Compiler Runtime R2023a. MCR is available
[here](https://nl.mathworks.com/products/compiler/matlab-runtime.html). To use
the local executable file, add the path to the executable file to the config
file. E.g.:

```
WorkDir=/home/username/tmp/stemmus_scope
...
ExeFilePath=/path/to/executable/STEMMUS_SCOPE
```

Alternatively, if the environmental variable `STEMMUS_SCOPE` is configured, the
BMI will use this if the ExeFilePath or DockerImage are not set in the
configuration file.

## Using the BMI

A [notebook demonstration the use of the Basic Model
Interface](notebooks/BMI_demo.ipynb) is available. For more information on using
BMI, see the [CSDMS website](https://csdms.colorado.edu/wiki/BMI).

If you need access to other model variables that are not yet available in the
BMI, please raise an issue on the [STEMMUS_SCOPE
repository](https://github.com/EcoExtreML/STEMMUS_SCOPE/issues), or leave a
comment if an issue is open already.

## Using grpc4bmi

A [Docker image is available](https://ghcr.io/ecoextreml/stemmus_scope-grpc4bmi)
in which the model as well as the Python BMI have been wrapped in a container.
The Docker image is created using the Docker file
[here](https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/blob/main/Dockerfile)
and allows communication with a STEMMUS_SCOPE BMI through
[grpc4bmi](https://grpc4bmi.readthedocs.io/en/latest/). Doing so avoids the
needs to install PyStemmusScope yourself, only Docker/apptainer and a python
environment with grpc4bmi are required. Please note you should not specify
`DockerImage` or `ExeFilePath` in the config file if you are using the grpc4bmi
interface. Only set the `STEMMUS_SCOPE` environmental variable with a path to
the executable file. A demonstration is available
[here](notebooks/grpc4bmi_demo.ipynb).

## Developer instructions

Follow the instructions in the `Contributing Guide`.
