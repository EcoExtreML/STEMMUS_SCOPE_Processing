"""The Docker STEMMUS_SCOPE model process wrapper."""
import os
import socket as pysocket
import warnings
from time import sleep
from typing import Any
from PyStemmusScope.bmi.docker_utils import check_tags
from PyStemmusScope.bmi.docker_utils import find_image
from PyStemmusScope.bmi.docker_utils import make_docker_vols_binds
from PyStemmusScope.bmi.utils import MATLAB_ERROR
from PyStemmusScope.bmi.utils import PROCESS_FINALIZED
from PyStemmusScope.bmi.utils import PROCESS_READY
from PyStemmusScope.bmi.utils import MatlabError
from PyStemmusScope.config_io import read_config


try:
    import docker
except ImportError:
    docker = None


def _model_is_ready(socket: Any, client: Any, container_id: Any) -> None:
    return _wait_for_model(PROCESS_READY, socket, client, container_id)


def _model_is_finalized(socket: Any, client: Any, container_id: Any) -> None:
    return _wait_for_model(PROCESS_FINALIZED, socket, client, container_id)


def _wait_for_model(phrase: bytes, socket: Any, client: Any, container_id: Any) -> None:
    """Wait for the model to be ready to receive (more) commands, or is finalized."""
    output = b""

    while phrase not in output:
        try:
            data = socket.read(1)
        except TimeoutError as err:
            client.stop(container_id)
            logs = client.logs(container_id).decode("utf-8")
            msg = (
                f"Container connection timed out '{container_id['Id']}'."
                f"\nPlease inspect logs:\n{logs}"
            )
            raise TimeoutError(msg) from err

        if data is None:
            msg = "Could not read data from socket. Docker container might be dead."
            raise ConnectionError(msg)
        else:
            output += bytes(data)

        if MATLAB_ERROR in output:
            client.stop(container_id)
            logs = client.logs(container_id).decode("utf-8")
            msg = (
                f"Error in container '{container_id['Id']}'.\n"
                f"Please inspect logs:\n{logs}"
            )
            raise MatlabError(msg)


def _attach_socket(client, container_id) -> Any:
    """Attach a socket to a container and add a timeout to it."""
    connection_timeout = 30  # seconds

    socket = client.attach_socket(container_id, {"stdin": 1, "stdout": 1, "stream": 1})
    if isinstance(socket, pysocket.SocketIO):
        socket._sock.settimeout(connection_timeout)  # type: ignore
    else:
        warnings.warn(
            message=(
                "Unknown socket type found. This might cause issues with the Docker"
                " connection. \nPlease report this to the developers in an issue "
                "on: https://github.com/EcoExtreML/STEMMUS_SCOPE_Processing/issues"
            ),
            stacklevel=1,
        )
    return socket


class StemmusScopeDocker:
    """Communicate with a STEMMUS_SCOPE Docker container."""

    # Default image, can be overridden with config:
    compatible_tags = ("1.5.0",)

    _process_ready_phrase = b"Select BMI mode:"
    _process_finalized_phrase = b"Finished clean up."

    def __init__(self, cfg_file: str):
        """Create the Docker container.."""
        self.cfg_file = cfg_file
        config = read_config(cfg_file)

        self.image = config["DockerImage"]
        find_image(self.image)
        check_tags(self.image, self.compatible_tags)

        self.client = docker.APIClient()

        vols, binds = make_docker_vols_binds(cfg_file)
        self.container_id = self.client.create_container(
            self.image,
            stdin_open=True,
            tty=True,
            detach=True,
            user=f"{os.getuid()}:{os.getgid()}",  # ensure correct user for writing files.
            volumes=vols,
            host_config=self.client.create_host_config(binds=binds),
        )

        self.running = False

    def _wait_for_model(self) -> None:
        """Wait for the model to be ready to receive (more) commands."""
        _model_is_ready(self.socket, self.client, self.container_id)

    def is_alive(self) -> bool:
        """Return if the process is alive."""
        return self.running

    def initialize(self) -> None:
        """Initialize the model and wait for it to be ready."""
        if self.is_alive():
            self.client.stop(self.container_id)

        self.client.start(self.container_id)
        self.socket = _attach_socket(self.client, self.container_id)

        self._wait_for_model()
        os.write(
            self.socket.fileno(),
            bytes(f'initialize "{self.cfg_file}"\n', encoding="utf-8"),
        )
        self._wait_for_model()

        self.running = True

    def update(self) -> None:
        """Update the model and wait for it to be ready."""
        if self.is_alive():
            os.write(self.socket.fileno(), b"update\n")
            self._wait_for_model()
        else:
            msg = "Docker container is not alive. Please restart the model."
            raise ConnectionError(msg)

    def finalize(self) -> None:
        """Finalize the model."""
        if self.is_alive():
            os.write(self.socket.fileno(), b"finalize\n")
            _model_is_finalized(
                self.socket,
                self.client,
                self.container_id,
            )
            sleep(0.5)  # Ensure the container can stop cleanly.
            self.client.stop(self.container_id)
            self.running = False
            self.client.remove_container(self.container_id, v=True)
        else:
            pass
