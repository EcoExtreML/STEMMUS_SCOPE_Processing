"""PyStemmusScope directories utilities.

Module designed to manage input directories and data for running the model
and storing outputs.
"""
import distutils.dir_util
import distutils.file_util
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

def read_config(path_to_config_file):
    """Read config from given config file.

    Load paths from config file and save them into dict.

    Args:
        path_to_config_file: Path to the config file.

    Returns:
        Dictionary containing paths to work directory and all sub-directories.
    """
    config = {}
    with open(path_to_config_file, "r", encoding="utf8") as f:
        for line in f:
            (key, val) = line.split("=")
            config[key] = val.rstrip('\n')

    return config

def create_io_dir(forcing_filename, config):
    """Create input directory and copy required files.

    Work flow executor to create work directory and all sub-directories.

    Returns:
        Path (string) to input, output directory and config file for every station/forcing.
    """
    # get start time with the format Y-M-D-HM
    timestamp = time.strftime('%Y%m%d_%H%M')
    station_name = forcing_filename.split('_')[0]
    # create input directory
    input_dir = Path(f"{config['WorkDir']}/input/{station_name}_{timestamp}")
    Path(input_dir).mkdir(parents=True, exist_ok=True)
    message = f"Prepare work directory {input_dir} for the station: {station_name}"
    logger.info("%s", message)
    # copy model parameters to work directory
    _copy_data(input_dir, config)
    input_dir = str(input_dir)

    # create output directory
    output_dir = Path(f"{config['WorkDir']}/output/{station_name}_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    message = f"Prepare work directory {output_dir} for the station: {station_name}"
    logger.info("%s", message)
    output_dir = str(output_dir)

    # update config file for ForcingFileName and InputPath
    config_file_path = _update_config_file(forcing_filename, input_dir, output_dir,
        config, station_name, timestamp)

    return input_dir, output_dir, config_file_path

def _copy_data(input_dir, config):
    """Copy required data to the work directory.

    Create sub-directories inside the work directory and copy data.

    Args:
        input_dir: Path to the input directory.
        config: Dictionary containing all the paths.
    """
    folder_list_vegetation = ["Directional", "FluspectParameters", "Leafangles",
        "Radiationdata", "SoilSpectra"]
    for folder in folder_list_vegetation:
        os.makedirs(input_dir / folder, exist_ok=True)
        distutils.dir_util.copy_tree(str(config[folder]), str(input_dir / folder))
    
    # copy input_data.xlsx
    distutils.file_util.copy_file(str(config["InputData"]), str(input_dir))

def _update_config_file(nc_file, input_dir, output_dir, config, station_name, timestamp): #pylint: disable=too-many-arguments
    """Update config file for each station.

    Create config file for each forcing/station under the work directory.
    
    Args:
        ncfile: Name of forcing file.
        input_dir: Path to the input directory.
        output_dir: Path to the output directory.
        config: Dictionary containing all the paths.
        station_name: Station name inferred from forcing file.
        timestamp: Timestamp when creating the config file.
    
    Returns:
        Path to updated config file.
    """
    config_file_path = Path(input_dir, f"{station_name}_{timestamp}_config.txt")
    with open(config_file_path, 'w', encoding="utf8") as f:
        for key, _ in config.items():
            if key == "ForcingFileName":
                f.write(key + "=" + nc_file + "\n")
            elif key == "InputPath":
                f.write(key + "=" + input_dir + "/" + "\n")
            elif key == "OutputPath":
                f.write(key + "=" + output_dir + "/" + "\n")
            else:
                f.write(key + "=" + key + "\n")        

    return str(config_file_path)