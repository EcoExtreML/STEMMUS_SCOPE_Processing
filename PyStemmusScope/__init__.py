"""Documentation about PyStemmusScope"""
import logging

from .iostreamer import read_config
from .iostreamer import create_io_dir

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Sarah Alidoost"
__email__ = "f.alidoost@esciencecenter.nl"
__version__ = "0.1.0"
