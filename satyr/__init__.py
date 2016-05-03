from __future__ import absolute_import, division, print_function

import logging
import pkg_resources as _pkg_resources

from .scheduler import QueueScheduler
from .executor import OneOffExecutor
from .messages import PythonTask, PythonTaskStatus  # important to register classes


logging.basicConfig(level=logging.DEBUG,
                    format='%(relativeCreated)6d %(threadName)s %(message)s')

__version__ = _pkg_resources.get_distribution('satyr').version

__all__ = ('QueueScheduler',
           'OneOffExecutor',
           'PythonTask',
           'PythonTaskStatus')
