# example config
config = {
    'id': 'thermos',
    'name': 'Thermos',
    'resources': {'cpus': 1, 'mem': 512},
    'max_tasks': 10,
    'master': '',
    'user': '',
    'executor_dir': '/path/on/the/worker/to/your/',
    'executor_file': 'executor.py' # optional
}
