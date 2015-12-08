from satyr import scheduler
import os

config = {
    'id': 'satyr',
    'name': 'Satyr',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 10,
    'master': '127.0.1.1:5050',
    'user': 'root',
    'executor_dir': '/rnd/satyr/',
    'executor_file': 'example_executor.py'
}

def handler(self, driver, executorId, slaveId, message):
    print message
    # To add more jobs: self.add_job('message')

echoer = scheduler.create_scheduler(config, handler, 'Initial job')
scheduler.run_scheduler(echoer)
