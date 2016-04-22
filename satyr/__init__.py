from __future__ import absolute_import, division, print_function

import logging
import pkg_resources as _pkg_resources

from .utils import configure_logging
from .scheduler import QueueScheduler
from .executor import OneOffExecutor
from .messages import PythonTask, PythonTaskStatus  # important to register classes


# log = logging.getLogger(__name__)
# configure_logging(True, log=log)

logging.basicConfig(level=logging.DEBUG,
                    format='%(relativeCreated)6d %(threadName)s %(message)s')
__version__ = _pkg_resources.get_distribution('satyr').version

# __all__ = ('BaseScheduler',
#            'BaseExecutor',
#            'PythonTask',
#            'PythonTaskStatus', 'log')
