"""Utility functions for making the docker process work."""
import warnings
from pathlib import Path
from PyStemmusScope.config_io import read_config


try:
    import docker
except ImportError:
    docker = None


def make_docker_vols_binds(cfg_file: str) -> tuple[list[str], list[str]]:
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
    if (not Path(cfg["InputPath"]).is_relative_to(cfg_dir)) or (
        Path(cfg["InputPath"]) == cfg_dir
    ):
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


def find_image(image: str) -> None:
    """See if the desired image is available, and if not, try to pull it."""
    client = docker.APIClient()
    images = client.images()
    tags = []
    for img in images:
        for tag in img["RepoTags"]:
            tags.append(tag)
    if image not in set(tags):
        pull_image(image)


def pull_image(image: str) -> None:
    """Pull the image from ghcr/dockerhub."""
    if ":" in image:
        image, tag = image.split(":")
    else:
        tag = None
    client = docker.from_env()
    image = client.images.pull(image, tag)
