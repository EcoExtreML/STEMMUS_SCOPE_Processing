%%% This script is an example that shows how to call user-defined Python module from MATLAB

%% activate the stemmus environment
pe = pyenv('Version','~/mamba/envs/stemmus/bin/python');

%% add the current folder to the Python search path
insert(py.sys.path,int64(0),'');

%% path to config file
config_file_path = "path_to_config_file_crib.txt";

%% read config file
config = py.example_python_modules.read_config(config_file_path);

%% create working directory
forcing_filename = config{'ForcingFileName'};
work_dir = py.example_python_modules.input_dir(forcing_filename, config);

%% path to model source code
model_source_codes = "path_to/STEMMUS_SCOPE/src";

%% add it to the top of your search path
addpath(model_source_codes);

%% run the model
STEMMUS_SCOPE_exe(config_file_path);

%% TODO csv to netcdf files