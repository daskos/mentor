from satyr import scheduler, executor
from mesos.interface import mesos_pb2
import time, os, sys


config = {
    'id': 'satyr',
    'name': 'Satyr',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 10,
    'master': '192.168.1.127:5050',
    'user': 'nagyz',
    'executor_dir': os.path.dirname(os.path.realpath(__file__)),
    'executor_file': 'example.py'
}


def run_on_scheduler(self, driver, executorId, slaveId, message):
    print message
    # To add more jobs: self.add_job('message')


def run_on_executor(self, driver, task):
    self.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)
    self.send_framework_message(driver, 'Sleep!')
    print 'sleeping...'
    time.sleep(3)
    self.send_framework_message(driver, 'Wake up!')
    self.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)


# With name it runs the scheduler otherwise the executor.
if __name__ == '__main__':
    if len(sys.argv) == 1:
        echoer = executor.create_executor(run_on_executor)
        executor.run_executor(echoer)
    else:
        config['name'] = sys.argv[1]
        echoer = scheduler.create_scheduler(config, run_on_scheduler, 'Initial job')
        scheduler.run_scheduler(echoer)
