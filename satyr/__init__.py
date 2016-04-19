from __future__ import absolute_import, division, print_function

import logging
import pkg_resources as _pkg_resources

from .utils import configure_logging
from .scheduler import BaseScheduler
from .executor import BaseExecutor
from .messages import PythonTask, PythonTaskStatus


log = logging.getLogger(__name__)
configure_logging(True, log=log)

__version__ = _pkg_resources.get_distribution('satyr').version

# __all__ = ('BaseScheduler',
#            'BaseExecutor',
#            'PythonTask',
#            'PythonTaskStatus', 'log')
