from thermos import executor
from mesos.interface import mesos_pb2
import time


def run_task(self, driver, task):
    self.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)
    print 'Let us sleep...'
    time.sleep(10)
    self.send_framework_message(driver, 'Wake up!')
    self.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)


echoer = executor.create_executor(run_task)
executor.run_executor(echoer)
