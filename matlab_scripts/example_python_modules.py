"""This script is an example that is used by the script run_model_in_matlab_dev.m"""

import shutil
from pathlib import Path
import time


def read_config(config_file_path):
    config = {}
    with open(config_file_path, "r", encoding="utf8") as f:
        for line in f:
            (key, val) = line.split("=")
            config[key] = val.rstrip('\n')
    return config


def input_dir(ncfile, config):
    """Create input directory and prepare input files
    """
    # get start time with the format Y-M-D-HM
    timestamp = time.strftime('%Y%m%d_%H%M')
    station_name = ncfile.split('_')[0]
    # create input directory
    work_dir = Path(f"{config['InputPath']}{station_name}_{timestamp}")
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    print(f"Prepare work directory {work_dir} for the station: {station_name}")
    # copy model parameters to work directory
    shutil.copytree(config["VegetationPropertyPath"], work_dir, dirs_exist_ok=True)
    # update config file for ForcingFileName and InputPath
    config_file_path = Path(work_dir, f"{station_name}_{timestamp}_config.txt")
    with open(config_file_path, 'w', encoding="utf8") as f:
        for i in config.keys():
            if i == "ForcingFileName":
                f.write(i + "=" + ncfile + "\n")
            elif i == "InputPath":
                f.write(i + "=" + str(work_dir) + "/" + "\n")
            else:
                f.write(i + "=" + config[i] + "\n")

    return str(work_dir)
