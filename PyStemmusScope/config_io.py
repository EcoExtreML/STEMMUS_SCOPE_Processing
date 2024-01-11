"""PyStemmusScope directories utilities.

Module designed to manage input directories and data for running the model
and storing outputs.
"""
import logging
import shutil
import time
from pathlib import Path
from typing import Union
from . import utils


logger = logging.getLogger(__name__)


def read_config(config_file: Union[str, Path]) -> dict[str, str]:
    """Read config from given config file.

    Load paths from config file and save them into dict.

    Args:
        config_file: Path to the config file.

    Returns:
        Dictionary containing paths to work directory and all sub-directories.
    """
    config = {}
    with Path(config_file).open(encoding="utf8") as f:
        for line in f:
            (key, val) = line.split("=")
            config[key] = val.rstrip("\n")

    validate_config(config)

    return config


def validate_config(config: Union[Path, dict]):
    """Validate the config file."""
    if isinstance(config, dict):
        cfg = config  # For proper type narrowing understood by Mypy.
    elif isinstance(config, Path):
        cfg = read_config(config)
    else:
        raise ValueError(
            "The input to validate_config should be either a Path or dict"
            f" object, but a {type(config)} object was passed."
        )

    # TODO: add check if the input data directories/file exist, and return clear error to user.
    _ = utils.check_location_fmt(cfg["Location"])
    utils.check_time_fmt(cfg["StartTime"], cfg["EndTime"])


def create_io_dir(config: dict) -> tuple[Path, Path, Path]:
    """Create input directory and copy required files.

    Work flow executor to create work directory and all sub-directories.

    Returns:
        Path to input, output directory and config file for every station/forcing.
    """
    # get start time with the format Y-M-D-HM
    timestamp = time.strftime("%Y-%m-%d-%H%M")

    loc, fmt = utils.check_location_fmt(config["Location"])
    if fmt == "site":
        site_name = loc
        input_dir_name = f"{loc}_{timestamp}"
    elif fmt == "latlon":
        site_name = "global"
        latstr = f"{loc[0]:.3f}".replace(".", "-")
        lonstr = f"{loc[1]:.3f}".replace(".", "-")
        latstr = f"N{latstr}" if loc[0] >= 0 else f"S{latstr[1:]}"  # type: ignore
        lonstr = f"E{lonstr}" if loc[1] >= 0 else f"W{lonstr[1:]}"  # type: ignore
        input_dir_name = f"global_{latstr}_{lonstr}_{timestamp}"
    else:
        raise NotImplementedError()

    # create input directory
    work_dir = utils.to_absolute_path(config["WorkDir"])
    input_dir = work_dir / "input" / input_dir_name
    input_dir.mkdir(parents=True, exist_ok=True)
    message = f"Prepare work directory {input_dir} for the location: {loc}"
    logger.info("%s", message)

    # copy model parameters to work directory
    _copy_data(input_dir, config)

    # create output directory
    output_dir = work_dir / "output" / input_dir_name
    output_dir.mkdir(parents=True, exist_ok=True)
    message = f"Prepare work directory {output_dir} for the location: {loc}"
    logger.info("%s", message)

    # update config file for ForcingFileName and InputPath
    config_file_path = _update_config_file(
        input_dir, output_dir, config, site_name, timestamp  # type: ignore
    )

    return input_dir, output_dir, config_file_path


def _copy_data(input_dir: Path, config: dict) -> None:
    """Copy required data to the work directory.

    Create sub-directories inside the work directory and copy data.

    Args:
        input_dir: Path to the input directory.
        config: Dictionary containing all the paths.
    """
    folder_list_vegetation = [
        "directional",
        "fluspect_parameters",
        "leafangles",
        "radiationdata",
        "soil_spectrum",
    ]
    for folder in folder_list_vegetation:
        (input_dir / folder).mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            str(config[folder]), str(input_dir / folder), dirs_exist_ok=True
        )

    # copy input_data.xlsx
    shutil.copy(str(config["input_data"]), str(input_dir))


def _update_config_file(
    input_dir: Path,
    output_dir: Path,
    config: dict,
    site_name: str,
    timestamp: str,
) -> Path:
    """Update config file for each station.

    Create config file for each forcing/station under the work directory.

    Args:
        input_dir: Path to the input directory.
        output_dir: Path to the output directory.
        config: Dictionary containing all the paths.
        site_name: The site name (eg. "FI-Hyy"), or "latlon" for global data.
        timestamp: Timestamp when creating the config file.

    Returns:
        Path to updated config file.
    """
    config_file_path = input_dir / f"{site_name}_{timestamp}_config.txt"
    with config_file_path.open(mode="w", encoding="utf8") as f:
        for key, value in config.items():
            if key == "InputPath":
                update_entry = f"{key}={str(input_dir)}/\n"
            elif key == "OutputPath":
                update_entry = f"{key}={str(output_dir)}/\n"
            else:
                update_entry = f"{key}={value}\n"

            f.write(update_entry)

    return config_file_path
