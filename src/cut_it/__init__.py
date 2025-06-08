"""Cut-It: Semantic text chunking tool for creating organized task lists."""

__version__ = "0.1.0"
__author__ = "Arthur Souza Rodrigues"
__email__ = "arthrod@umich.edu"

from .splitter import TextProcessor
from .formatter import TaskFormatter

__all__ = ["TextProcessor", "TaskFormatter"]