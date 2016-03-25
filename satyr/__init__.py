import logging
log = logging.getLogger('satyr')

import pkg_resources as _pkg_resources
__version__ = _pkg_resources.get_distribution('satyr').version
