<img align="right" width="200" alt="Logo" src="ecoextreml_logo.png">

# Getting started

This is the documentation for the python package `PyStemmusScope`, which allows
for preparing data and running the STEMMUS-SCOPE model. The model source code
[STEMMUS_SCOPE repository](https://github.com/EcoExtreML/STEMMUS_SCOPE).

## Requirements

To run the model, check the
[requirements](https://ecoextreml.github.io/STEMMUS_SCOPE/getting_started/).

## Configuration file

The configuration file is a text file that sets the paths required by the model.
Check [**required** information and
templates](https://ecoextreml.github.io/STEMMUS_SCOPE/getting_started/#configuration-file).
In addition to required information, there are optional parameters that can be
set in the configuration file:

- `soil_layers_thickness`: a path to a csv file containing soil layers thickness
  information, see
  [exmaple](https://github.com/EcoExtreML/STEMMUS_SCOPE/blob/main/example_data/input_soilLayThick.csv).
- `ExeFilePath`: a path to the STEMMUS-SCOPE executable file, if BMI interface
  is used.
- `DockerImage`: a path to the Docker image, if BMI interface and docker are
  used.

## Running the model

If you want to run the model using `PyStemmusScope`, follow the instructions in
the `installation` and `Run the model` documentation.

If you want to add changes to the package `PyStemmusScope`, follow `Contributing
guide` documnetation.
