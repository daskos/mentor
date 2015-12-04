from mesos.interface import Executor, mesos_pb2
from mesos.native import MesosExecutorDriver
from skeleton import Skeleton, create_driver_method
import sys, threading


class ThermosExecutor(Executor, Skeleton):
    ALLOWED_HANDLERS = ['runTask']

    def launchTask(self, driver, task):
        thread = threading.Thread(target=self.runTask, args=(driver, task))
        #thread.daemon = True
        thread.start()

    def create_status_update(self, task, state):
        update = mesos_pb2.TaskStatus()
        update.task_id.value = task.task_id.value
        update.state = state
        return update

    def send_status_update(self, driver, task, state):
        driver.sendStatusUpdate(self.create_status_update(task, state))

    def send_framework_message(self, driver, message):
        driver.sendFrameworkMessage(message)


def create_executor(run_task_handler):
    executor = ThermosExecutor()
    executor.add_handler('runTask', run_task_handler)
    return MesosExecutorDriver(executor)


def run_executor(executor):
    method = create_driver_method(executor)
    method()
