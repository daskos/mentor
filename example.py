import os
import sys
import time

from mesos.interface import mesos_pb2
from satyr import executor
from satyr.scheduler import SatyrScheduler

config = {
    'id': 'satyr',
    'name': 'Satyr',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 10,
    'master': '192.168.1.80:5050',
    'user': 'nagyz',
    'filter_refuse_seconds': 10,
    'permanent': False,
    'command': 'python %s/example.py' % os.path.dirname(os.path.realpath(__file__))
}


def run_on_scheduler(scheduler, driver, executorId, slaveId, data):
    print data


def run_on_executor(executor, driver, task):
    executor.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)
    executor.send_framework_message(driver, 'Sleep!')
    print 'sleeping...'
    time.sleep(3)
    executor.send_framework_message(driver, 'Wake up!')
    executor.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)


# With name it runs the scheduler otherwise the executor.
if __name__ == '__main__':
    if len(sys.argv) == 1:
        echoer = executor.create_executor(run_on_executor)
        executor.run_executor(echoer)
    else:
        s = SatyrScheduler(config, run_on_scheduler)
        s.add_job({'some': 'stuff'})
        s.run()
