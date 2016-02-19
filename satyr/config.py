import os
from .executors import pickled as pickled_executor
from copy import copy

default = {
    'id': 'satyr',
    'name': 'Satyr',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 1,
    'master': '192.168.1.127:5050',
    'user': 'root',
    'executor_dir': os.path.dirname(pickled_executor.__file__),
    'executor_file': 'pickled.py',
    'command': 'python -m satyr.executors.pickled',
    'permanent': False,
    'filter_refuse_seconds': 300
}


class Config(dict):
    def __init__(self, conf={}):
        """Reading config, always overwriting any value w/ the ones
        set in environment variables started as SATYR_."""
        d = copy(default)
        d.update(conf)
        for k, v in d.items():
            setattr(self, k, os.getenv('SATYR_' + k.upper(), v))

    def __getitem__(self, key):
        return getattr(self, key)
