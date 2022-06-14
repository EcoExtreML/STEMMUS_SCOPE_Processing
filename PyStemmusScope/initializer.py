from pathlib import Path
import os
import time
import shutil


class InputDir:
    """Create input directories and copy required data."""

    def __init__(self, path_to_config_file: str = "config_file_snellius.txt",
        path_to_model: str = "path_to_STEMMUS_SCOPE_repository"
    ):
        """Instantiate a handler for working directories

        Specify path STEMMUS SCOPE repository and load the config file.

        """
    
        self.config = self._read_config(path_to_config_file)
        self.path_to_model = path_to_model

    def _read_config(self, path_to_config_file):
        """Read config from given config file."""
        config = {}
        with open(path_to_config_file, "r") as f:
            for line in f:
                (key, val) = line.split("=")
                config[key] = val.rstrip('\n')

        return config

    def prepare_work_dir(self, forcing_filenames_list: list = [],
        full_run: bool = False
    ):
        """Prepare work directory"""
        self.forcing_filenames_list = forcing_filenames_list
        
        if full_run:
            self.forcing_filenames_list = [file.name for file in Path(self.config["ForcingPath"]).iterdir()]

        # dict to store path to config file and working directory for each station
        self.work_dir_dict, self.config_path_dict = self._create_work_dir()

        return self.work_dir_dict, self.config_path_dict

    def _create_work_dir(self):
        """Create input directory and copy forcing files."""
        # empty dict to store path to config file and working directory for each station
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
        """Copy required data to the work directory."""
        folder_list_vegetation = ["Directional", "FluspectParameters", "Leafangles",
            "Radiationdata", "SoilSpectra"]
        for folder in folder_list_vegetation:
            os.makedirs(work_dir / folder, exist_ok=True)
            shutil.copytree(self.config[folder], work_dir / folder, dirs_exist_ok=True)
        
        # copy input_data.xlsx
        shutil.copy(self.config["InputData"], work_dir)

    def _update_config_file(self, ncfile, work_dir, station_name, timestamp):
        """Update config file for each station."""
        config_file_path = Path(work_dir, f"{station_name}_{timestamp}_config.txt")
        with open(config_file_path, 'w') as f:
            for i in self.config.keys():
                if i == "ForcingFileName":
                    f.write(i + "=" + ncfile + "\n")
                elif i == "InputPath":
                    f.write(i + "=" + str(work_dir) + "/" + "\n")
                else:
                    f.write(i + "=" + self.config[i] + "\n")        

        return config_file_path
