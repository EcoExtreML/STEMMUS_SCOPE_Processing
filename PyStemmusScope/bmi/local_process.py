"""The local STEMMUS_SCOPE model process wrapper."""
import os
import platform
import subprocess
from pathlib import Path
from time import sleep
from typing import Union
from PyStemmusScope.bmi.utils import MATLAB_ERROR
from PyStemmusScope.bmi.utils import PROCESS_READY
from PyStemmusScope.bmi.utils import MatlabError
from PyStemmusScope.config_io import read_config


def alive_process(
    process: Union[subprocess.Popen, None]
) -> subprocess.Popen:  # pragma: no cover
    """Return process if the process is alive, raise an exception if it is not."""
    if process is None:
        msg = "Model process does not seem to be open."
        raise ConnectionError(msg)
    if process.poll() is not None:
        msg = f"Model terminated with return code {process.poll()}"
        raise ConnectionError(msg)
    return process


def read_stdout(process: subprocess.Popen) -> bytes:  # pragma: no cover
    """Read from stdout. If the stream ends unexpectedly, an error is raised."""
    assert process.stdout is not None  # required for type narrowing.
    read = process.stdout.read(1)

    retries = 0
    retry_time = 0.1
    while read is None:
        sleep(retry_time)
        read = process.stdout.read(1)
        retries += 1
        if retries > int(60 / retry_time):
            msg = "Connection error: could not find expected output or "
            raise ConnectionError(msg)
    return bytes(read)


def _model_is_ready(process: subprocess.Popen) -> None:  # pragma: no cover
    return _wait_for_model(PROCESS_READY, process)


def _wait_for_model(
    phrase: bytes, process: subprocess.Popen
) -> None:  # pragma: no cover
    """Wait for model to be ready for interaction."""
    output = b""

    while alive_process(process) and phrase not in output:
        output += read_stdout(process)
        if MATLAB_ERROR in output:
            try:
                process.terminate()
            finally:
                msg = (
                    "Error encountered in Matlab.\n"
                    "Please inspect logs in the output directory"
                )
                raise MatlabError(msg)


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


class LocalStemmusScope:  # pragma: no cover
    """Communicate with the local STEMMUS_SCOPE executable file."""

    def __init__(self, cfg_file: str) -> None:
        """Initialize the process."""
        self.cfg_file = cfg_file
        config = read_config(cfg_file)

        exe_file = find_exe(config)
        args = [exe_file, cfg_file, "bmi"]

        lib_path = os.getenv("LD_LIBRARY_PATH")
        if lib_path is None:
            msg = (
                "Environment variable LD_LIBRARY_PATH not found. "
                "Refer the Matlab Compiler Runtime documentation"
            )
            raise ValueError(msg)

        # Ensure output directory exists so log file can be written:
        Path(config["OutputPath"]).mkdir(parents=True, exist_ok=True)
        env = {
            "LD_LIBRARY_PATH": lib_path,
            "MATLAB_LOG_DIR": str(config["OutputPath"]),
        }

        self.process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            bufsize=0,
            env=env,
        )

        if platform.system() == "Linux":
            assert self.process.stdout is not None  # required for type narrowing.
            # Make the connection non-blocking to allow for a timeout on read.
            os.set_blocking(self.process.stdout.fileno(), False)
        else:
            msg = "Unexpected system. The executable is only compiled for Linux."
            raise ValueError(msg)
        _model_is_ready(self.process)

    def is_alive(self) -> bool:
        """Return if the process is alive."""
        try:
            alive_process(self.process)
            return True
        except ConnectionError:
            return False

    def initialize(self) -> None:
        """Initialize the model and wait for it to be ready."""
        self.process = alive_process(self.process)

        self.process.stdin.write(  # type: ignore
            bytes(f'initialize "{self.cfg_file}"\n', encoding="utf-8")
        )
        _model_is_ready(self.process)

    def update(self) -> None:
        """Update the model and wait for it to be ready."""
        if self.process is None:
            msg = "Run initialize before trying to update the model."
            raise AttributeError(msg)

        self.process = alive_process(self.process)
        self.process.stdin.write(b"update\n")  # type: ignore
        _model_is_ready(self.process)

    def finalize(self) -> None:
        """Finalize the model."""
        self.process = alive_process(self.process)
        self.process.stdin.write(b"finalize\n")  # type: ignore
        sleep(10)
        if self.process.poll() != 0:
            try:
                self.process.terminate()
            finally:
                msg = f"Model terminated with return code {self.process.poll()}"
                raise ValueError(msg)
