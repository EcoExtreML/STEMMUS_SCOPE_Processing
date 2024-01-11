"""The local STEMMUS_SCOPE model process wrapper."""
import os
import subprocess
from pathlib import Path
from typing import Union
from PyStemmusScope.config_io import read_config


def is_alive(process: Union[subprocess.Popen, None]) -> subprocess.Popen:
    """Return process if the process is alive, raise an exception if it is not."""
    if process is None:
        msg = "Model process does not seem to be open."
        raise ConnectionError(msg)
    if process.poll() is not None:
        msg = f"Model terminated with return code {process.poll()}"
        raise ConnectionError(msg)
    return process


def wait_for_model(process: subprocess.Popen, phrase=b"Select BMI mode:") -> None:
    """Wait for model to be ready for interaction."""
    output = b""
    while is_alive(process) and phrase not in output:
        assert process.stdout is not None  # required for type narrowing.
        output += bytes(process.stdout.read(1))


def find_exe(config: dict) -> str:
    """Find the right path to the executable file."""
    if "ExeFilePath" in config:
        exe_file = config["ExeFilePath"]
    elif os.getenv("STEMMUS_SCOPE") is not None:
        exe_file = os.getenv("STEMMUS_SCOPE")
    else:
        msg = "No STEMMUS_SCOPE executable found."
        raise ValueError(msg)
    if not Path(exe_file).exists():
        msg = f"No file found at {exe_file}"
        raise FileNotFoundError(exe_file)
    return exe_file


class LocalStemmusScope:
    """Communicate with the local STEMMUS_SCOPE executable file."""

    def __init__(self, cfg_file: str) -> None:
        """Initialize the process."""
        self.cfg_file = cfg_file
        config = read_config(cfg_file)

        exe_file = find_exe(config)
        args = [exe_file, cfg_file, "bmi"]

        os.environ["MATLAB_LOG_DIR"] = str(config["InputPath"])

        self.matlab_process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0,
        )

        wait_for_model(self.matlab_process)

    def is_alive(self) -> bool:
        """Return if the process is alive."""
        try:
            is_alive(self.matlab_process)
            return True
        except ConnectionError:
            return False

    def initialize(self) -> None:
        """Initialize the model and wait for it to be ready."""
        self.matlab_process = is_alive(self.matlab_process)

        self.matlab_process.stdin.write(  # type: ignore
            bytes(f'initialize "{self.cfg_file}"\n', encoding="utf-8")
        )
        wait_for_model(self.matlab_process)

    def update(self) -> None:
        """Update the model and wait for it to be ready."""
        if self.matlab_process is None:
            msg = "Run initialize before trying to update the model."
            raise AttributeError(msg)

        self.matlab_process = is_alive(self.matlab_process)
        self.matlab_process.stdin.write(b"update\n")  # type: ignore
        wait_for_model(self.matlab_process)

    def finalize(self) -> None:
        """Finalize the model."""
        self.matlab_process = is_alive(self.matlab_process)
        self.matlab_process.stdin.write(b"finalize\n")  # type: ignore
        wait_for_model(self.matlab_process, phrase=b"Finished clean up.")
