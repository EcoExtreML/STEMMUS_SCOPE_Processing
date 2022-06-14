"""PyStemmusScope directories utilities.

Module designed to manage input directories and data for running the model
and storing outputs.
"""
from pathlib import Path
import os
import time
import distutils.dir_util
import distutils.file_util


class InputDir:
    """Create input directories and copy required data."""

    def __init__(self, path_to_config_file: str = "config_file_snellius.txt",
        path_to_model: str = "path_to_STEMMUS_SCOPE_repository"
    ):
        """Instantiate a handler for work directories.

        Specify path STEMMUS SCOPE repository and load the config file.

        Args:
            path_to_config_file: Path to the config file.
            path_to_model: Path to the model.
        """
    
        self.config = self._read_config(path_to_config_file)
        self.path_to_model = path_to_model

    def __str__(self):
        return "Input directories handler."

    def _read_config(self, path_to_config_file):
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

    def prepare_work_dir(self, forcing_filenames_list: list,
        full_run: bool = False
    ):
        """Prepare work directory for each station.

        Prepare work directory based on the given list of forcing. This function
        creates directory for each forcing data and name it using the name of the
        station.

        Args:
            forcing_filenames_list: List of forcing filenames to be used for the experiments.
            full_run: If true, all stations with forcing listed in the ForcingPath will be used.

        Returns:
            Dictionary containing path to work directory and config file for every station/forcing.
        """
        self.forcing_filenames_list = forcing_filenames_list
        
        if full_run:
            self.forcing_filenames_list = [file.name for file in Path(self.config["ForcingPath"]).iterdir()]

        # dict to store path to config file and work directory for each station
        self.work_dir_dict, self.config_path_dict = self._create_work_dir()

        return self.work_dir_dict, self.config_path_dict

    def _create_work_dir(self):
        """Create input directory and copy forcing files.

        Work flow executor to create work directory and all sub-directories.

        Returns:
            Dictionary containing path to work directory and config file for every station/forcing.
        """
        # empty dict to store path to config file and work directory for each station
        config_path_dict = {}
        work_dir_dict = {}
        for ncfile in self.forcing_filenames_list:
            # get start time with the format Y-M-D-HM
            timestamp = time.strftime('%Y%m%d_%H%M')
            station_name = ncfile.split('_')[0]
            # create input directory
            work_dir = Path(self.config["InputPath"], station_name + '_' + timestamp)
            Path(work_dir).mkdir(parents=True, exist_ok=True)
            print(f"Prepare work directory {work_dir} for the station: {station_name}")
            # copy model parameters to work directory
            self._copy_data(work_dir)
            # update config file for ForcingFileName and InputPath
            config_file_path = self._update_config_file(ncfile, work_dir, station_name, timestamp)
            # save config path and work directory to the dictionaries
            work_dir_dict[ncfile] = work_dir
            config_path_dict[ncfile] = config_file_path

        return work_dir_dict, config_path_dict

    def _copy_data(self, work_dir):
        """Copy required data to the work directory.

        Create sub-directories inside the work directory and copy data.

        Args:
            work_dir: Path to the work directory.
        """
        folder_list_vegetation = ["Directional", "FluspectParameters", "Leafangles",
            "Radiationdata", "SoilSpectra"]
        for folder in folder_list_vegetation:
            os.makedirs(work_dir / folder, exist_ok=True)
            distutils.dir_util.copy_tree(str(self.config[folder]), str(work_dir / folder))
        
        # copy input_data.xlsx
        distutils.file_util.copy_file(str(self.config["InputData"]), str(work_dir))

    def _update_config_file(self, ncfile, work_dir, station_name, timestamp):
        """Update config file for each station.

        Create config file for each forcing/station under the work directory.
        
        Args:
            ncfile: Name of forcing file.
            work_dir: Path to the work directory.
            station_name: Station name inferred from forcing file.
            timestamp: Timestamp when creating the config file.
        
        Returns:
            Path to updated config file.
        """
        config_file_path = Path(work_dir, f"{station_name}_{timestamp}_config.txt")
        with open(config_file_path, 'w', encoding="utf8") as f:
            for i in self.config.items():
                if i[0] == "ForcingFileName":
                    f.write(i[0] + "=" + ncfile + "\n")
                elif i == "InputPath":
                    f.write(i[0] + "=" + str(work_dir) + "/" + "\n")
                else:
                    f.write(i[0] + "=" + i[1] + "\n")        

        return config_file_path
