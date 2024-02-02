import warnings
import pytest
from PyStemmusScope.bmi import docker_utils


def test_check_tags():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        docker_utils.check_tags(
            image="ghcr.io/ecoextreml/stemmus_scope:1.5.0",
            compatible_tags=("1.5.0"),
        )


def test_check_missing_tag():
    with pytest.warns(UserWarning, match="no tag was provided"):
        docker_utils.check_tags(
            image="ghcr.io/ecoextreml/stemmus_scope",
            compatible_tags=("none"),
        )


def test_incompatible_tag():
    with pytest.warns(UserWarning, match="unexpected results"):
        docker_utils.check_tags(
            image="ghcr.io/ecoextreml/stemmus_scope:1.6.0",
            compatible_tags=("1.5.0", "1.5.1"),
        )
