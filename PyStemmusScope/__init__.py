"""Documentation about PyStemmusScope"""
import logging
from . import forcing_io
from . import iostreamer
from .iostreamer import create_io_dir
from .iostreamer import read_config


logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Sarah Alidoost"
__email__ = "f.alidoost@esciencecenter.nl"
__version__ = "0.1.0"
