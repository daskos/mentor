from thermos import scheduler
import os

config = {
    'id': 'thermos',
    'name': 'Thermos',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 10,
    'master': '127.0.1.1:5050',
    'user': 'root',
    'executor_dir': '/rnd/thermos/',
    'executor_file': 'example_executor.py'
}

def handler(self, driver, executorId, slaveId, message):
    print message
    #self.task_queue.append('message')

echoer = scheduler.create_scheduler(config, handler)
scheduler.run_scheduler(echoer)
