from __future__ import absolute_import, division, print_function

import atexit
import logging
import threading

from mesos.interface import mesos_pb2
from mesos.native import MesosExecutorDriver

from .interface import Executor
from .proxies import ExecutorProxy


class BaseExecutor(Executor):

    """Base class for Mesos executors.

    Users' executors should extend this class to get default implementations of
    methods they don't override.
    """

    def __call__(self):
        return self.run()

    def run(self):
        # TODO logging
        driver = MesosExecutorDriver(ExecutorProxy(self))
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        return status

    def on_launch(self, driver, task):
        def run_task():
            driver.update(task.status('TASK_RUNNING'))

            try:
                result = task()
            except Exception as e:
                driver.update(task.status('TASK_FAILED', message=e.message))
            else:
                driver.update(task.status('TASK_FINISHED', data=result))

        thread = threading.Thread(target=run_task)
        thread.start()

    def on_kill(self, driver, task_id):
        driver.stop()


if __name__ == '__main__':
    BaseExecutor().run()
