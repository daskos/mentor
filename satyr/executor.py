from __future__ import absolute_import, division, print_function

import atexit
import logging
import signal
import sys
import threading
from functools import partial

from mesos.interface import mesos_pb2
from mesos.native import MesosExecutorDriver

from .interface import Executor
from .messages import PythonTaskStatus
from .proxies import ExecutorProxy


class Running(object):

    def __init__(self, executor):
        executor = ExecutorProxy(executor)
        self.driver = MesosExecutorDriver(executor)

        def shutdown(signal, frame):
            self.stop()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
        atexit.register(self.stop)

    def run(self):
        return self.driver.run()

    def start(self):
        status = self.driver.start()
        assert status == mesos_pb2.DRIVER_RUNNING
        return status

    def stop(self):
        return self.driver.stop()

    def join(self):
        return self.driver.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.join()
        if exc_type:
            raise exc_type, exc_value, traceback


class OneOffExecutor(Executor):

    def on_launch(self, driver, task):
        status = partial(PythonTaskStatus, task_id=task.id)

        def run_task():
            driver.update(status(state='TASK_RUNNING'))
            logging.info('Sent TASK_RUNNING status update')

            try:
                logging.info('Executing task...')
                result = task()
            except Exception as e:
                logging.exception('Task errored')
                driver.update(status(state='TASK_FAILED',
                                     data=e, message=e.message))
                logging.info('Sent TASK_RUNNING status update')
            else:
                driver.update(status(state='TASK_FINISHED', data=result))
                logging.info('Sent TASK_FINISHED status update')
            finally:
                # stopper = threading.Timer(1.0, driver.stop)
                # stopper.start()
                driver.stop()

        thread = threading.Thread(target=run_task)
        thread.start()

    def on_kill(self, driver, task_id):
        driver.stop()

    def on_shutdown(self, driver):
        driver.stop()


if __name__ == '__main__':
    status = Running(OneOffExecutor()).run()
    code = 0 if status == mesos_pb2.DRIVER_STOPPED else 1
    sys.exit(code)
