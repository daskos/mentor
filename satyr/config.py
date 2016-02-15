import os
from .executors import pickled as pickled_executor

default = {
    'id': 'satyr',
    'name': 'Satyr',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 1,
    'master': '192.168.1.127:5050',
    'user': 'root',
    'executor_dir': os.path.dirname(pickled_executor.__file__),
    'executor_file': 'pickled.py',
    'permanent': False
}
