"""Documentation about PyStemmusScope."""
import logging
from .stemmus_scope import StemmusScope


logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["StemmusScope"]

__author__ = "Sarah Alidoost"
__email__ = "f.alidoost@esciencecenter.nl"
__version__ = "0.4.0"
