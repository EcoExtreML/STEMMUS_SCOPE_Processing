"""The Docker STEMMUS_SCOPE model process wrapper."""
from PyStemmusScope.config_io import read_config
from pathlib import Path
import os
import docker


def make_docker_vols_binds(cfg_file: str) -> tuple[list[str], list[str]]:
    """Make docker volume mounting configs.

    Args:
        cfg_file: Location of the config file

    Returns:
        volumes, binds
    """
    cfg = read_config(cfg_file)
    
    volumes = [cfg["OutputPath"], cfg["InputPath"]]
    binds = [
        f"{cfg['OutputPath']}:{cfg['OutputPath']}:rw",
        f"{cfg['InputPath']}:{cfg['InputPath']}:ro",
    ]

    if (
        not Path(cfg_file).parent.is_relative_to(cfg["InputPath"]) or
        not Path(cfg_file).parent.is_relative_to(cfg["OutputPath"])
    ):
        cfg_folder = str(Path(cfg_file).parent)
        volumes.append(cfg_folder)
        binds.append(f"{cfg_folder}:{cfg_folder}:ro")

    return volumes, binds


class StemmusScopeDocker:
    """Communicate with a STEMMUS_SCOPE Docker container."""
    # The image is hard coded here to ensure compatiblity:
    image = "ghcr.io/ecoextreml/stemmus_scope:1.5.0"

    _process_ready_phrase = b"Select BMI mode:"

    def __init__(self, cfg_file: str):
        """Create the Docker container.."""
        self.cfg_file = cfg_file
        
        self.client = docker.APIClient()

        vols, binds = make_docker_vols_binds(cfg_file)
        self.container_id = self.client.create_container(
            self.image,
            stdin_open=True,
            tty=True,
            detach=True,
            volumes=vols,
            host_config=self.client.create_host_config(binds=binds)
        )
        
        self.running = False
    
    def wait_for_model(self):
        """Wait for the model to be ready to receive (more) commands."""
        output = b""

        while self._process_ready_phrase not in output:
            data = self.socket.read(1)
            if data is None:
                msg = "Could not read data from socket. Docker container might be dead."
                raise ConnectionError(msg)
            else:
                output += bytes(data)
    
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
        else:
            pass
