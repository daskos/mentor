from mesos.interface import Executor, mesos_pb2
from mesos.native import MesosExecutorDriver
from skeleton import Skeleton, create_driver_method
import threading


class SatyrExecutor(Executor, Skeleton):
    ALLOWED_HANDLERS = ['runTask']

    def launchTask(self, driver, task):
        driver.sendStatusUpdate(self.create_status_update(task, mesos_pb2.TASK_STARTING))
        thread = threading.Thread(target=self.runTask, args=(driver, task))
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
    executor = SatyrExecutor()
    executor.add_handler('runTask', run_task_handler)
    return executor


def run_executor(executor):
    method = create_driver_method(MesosExecutorDriver(executor))
    return method()
