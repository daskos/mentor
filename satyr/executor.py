import threading

from mesos.interface import Executor, mesos_pb2
from mesos.native import MesosExecutorDriver
from skeleton import Skeleton, create_driver_method


class SatyrExecutor(Executor, Skeleton):
    ALLOWED_HANDLERS = ['runTask']

    def __init__(self, run_task):
        self.run_task = run_task

    def launchTask(self, driver, task):
        driver.sendStatusUpdate(self.create_status_update(
            task, mesos_pb2.TASK_STARTING))
        thread = threading.Thread(target=self.run_task, args=(self, driver, task))
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

    def run(self):
        method = create_driver_method(MesosExecutorDriver(self))
        return method()
