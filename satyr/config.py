from __future__ import absolute_import, division, print_function

import os
from copy import copy


default = {
    'id': 'satyr',
    'name': 'Satyr',
    'user': 'root',
    'master': '192.168.1.127:5050',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 1,
    'command': 'python -m satyr.executors.pickled',
    'filter_refuse_seconds': 5,
    'permanent': False
}
