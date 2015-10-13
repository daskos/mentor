from mesos.interface import Executor, mesos_pb2
from mesos.native import MesosExecutorDriver
from skeleton import Skeleton, create_driver_method
import sys


class ThermosExecutor(Executor, Skeleton):
    ALLOWED_HANDLERS = ['run_task']


def create_executor(framework_message_handler):
    executor = ThermosExecutor()
    executor.add_handler('run_task', framework_message_handler)
    return MesosExecutorDriver(executor)


def run_executor(executor):
    method = create_driver_method(executor)
    method()
