from __future__ import absolute_import, division, print_function

import logging

from .utils import configure_logging

log = logging.getLogger('satyr')
configure_logging(True, log=log)

import pkg_resources as _pkg_resources
__version__ = _pkg_resources.get_distribution('satyr').version
