"""The Docker STEMMUS_SCOPE model process wrapper."""
from time import sleep
from typing import Any, List, Tuple
import warnings
from PyStemmusScope.config_io import read_config
from pathlib import Path
import os

try:
    import docker
except ImportError:
    docker = None


def make_docker_vols_binds(cfg_file: str) -> Tuple[List[str], List[str]]:
    """Make docker volume mounting configs.

    Args:
        cfg_file: Location of the config file

    Returns:
        volumes, binds
    """
    cfg = read_config(cfg_file)
    cfg_dir = Path(cfg_file).parent
    volumes = []
    binds = []

    # Make sure no subpaths are mounted:
    if not cfg_dir.is_relative_to(cfg["InputPath"]):
        volumes.append(str(cfg_dir))
        binds.append(f"{str(cfg_dir)}:{str(cfg_dir)}")
    if (not Path(cfg["InputPath"]).is_relative_to(cfg_dir)) or (Path(cfg["InputPath"]) == cfg_dir):
        volumes.append(cfg["InputPath"])
        binds.append(f"{cfg['InputPath']}:{cfg['InputPath']}")
    if not Path(cfg["OutputPath"]).is_relative_to(cfg_dir):
        volumes.append(cfg["OutputPath"])
        binds.append(f"{cfg['OutputPath']}:{cfg['OutputPath']}")

    return volumes, binds


def check_tags(image: str, compatible_tags: tuple[str, ...]):
    """Check if the tag is compatible with this version of the BMI.

    Args:
        image: The full image name (including tag)
        compatible_tags: Tags which are known to be compatible with this version of the
            BMI.
    """
    if ":" not in image:
        msg = (
            "Could not validate the Docker image tag, as no tag was provided.\n"
            "Please set the Docker image tag in the configuration file."
        )
        warnings.warn(UserWarning(msg), stacklevel=1)

    tag = image.split(":")[-1]
    if tag not in compatible_tags:
        msg = (
            f"Docker image tag '{tag}' not found in compatible tags "
            f"({compatible_tags}).\n"
            "You might experience issues or unexpected results."
        )
        warnings.warn(UserWarning(msg), stacklevel=1)


def wait_for_model(phrase: bytes, socket: Any) -> None:
    """Wait for the model to be ready to receive (more) commands, or is finalized."""
    output = b""

    while phrase not in output:
        data = socket.read(1)
        if data is None:
            msg = "Could not read data from socket. Docker container might be dead."
            raise ConnectionError(msg)
        else:
            output += bytes(data)


class StemmusScopeDocker:
    """Communicate with a STEMMUS_SCOPE Docker container."""
    # Default image, can be overridden with config:
    compatible_tags = ("1.5.0", )

    _process_ready_phrase = b"Select BMI mode:"
    _process_finalized_phrase = b"Finished clean up."

    def __init__(self, cfg_file: str):
        """Create the Docker container.."""
        self.cfg_file = cfg_file
        config = read_config(cfg_file)

        self.image = config["DockerImage"]
        check_tags(self.image, self.compatible_tags)

        self.client = docker.APIClient()

        vols, binds = make_docker_vols_binds(cfg_file)
        self.container_id = self.client.create_container(
            self.image,
            stdin_open=True,
            tty=True,
            detach=True,
            user=os.getuid(),  # ensure correct user for writing files.
            volumes=vols,
            host_config=self.client.create_host_config(binds=binds)
        )

        self.running = False
    
    def wait_for_model(self):
        """Wait for the model to be ready to receive (more) commands."""
        wait_for_model(self._process_ready_phrase, self.socket)
    
    def is_alive(self):
        """Return if the process is alive."""
        return self.running
    
    def initialize(self):
        """Initialize the model and wait for it to be ready."""
        if self.is_alive():
            self.client.stop(self.container_id)

        self.client.start(self.container_id)
        self.socket = self.client.attach_socket(
            self.container_id, {'stdin': 1, 'stdout': 1, 'stream':1}
        )
        self.wait_for_model()
        os.write(
            self.socket.fileno(),
            bytes(f'initialize "{self.cfg_file}"\n', encoding="utf-8")
        )
        self.wait_for_model()

        self.running = True

    def update(self):
        """Update the model and wait for it to be ready."""
        if self.is_alive():
            os.write(
                self.socket.fileno(),
                b'update\n'
            )
            self.wait_for_model()
        else:
            msg = "Docker container is not alive. Please restart the model."
            raise ConnectionError(msg)

    def finalize(self):
        """Finalize the model."""
        if self.is_alive():
            os.write(self.socket.fileno(),b'finalize\n')
            wait_for_model(self._process_finalized_phrase, self.socket)
            sleep(0.5)  # Ensure the container can stop cleanly.
            self.client.stop(self.container_id)
            self.client.remove_container(self.container_id, v=True)
        else:
            pass
