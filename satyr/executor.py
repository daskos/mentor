from __future__ import absolute_import, division, print_function

import atexit
import logging
import signal
import sys
import threading

from mesos.interface import mesos_pb2
from mesos.native import MesosExecutorDriver

from .interface import Executor
from .proxies import ExecutorProxy


class Running(object):

    def __init__(self, executor):
        executor = ExecutorProxy(executor)
        self.driver = MesosExecutorDriver(executor)

        def shutdown(signal, frame):
            self.driver.stop()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
        atexit.register(self.driver.stop)

    def run(self):
        return self.driver.run()

    def start(self):
        status = self.driver.start()
        assert status == mesos_pb2.DRIVER_RUNNING
        return status

    def stop(self):
        logging.info("Stopping Mesos driver")
        self.driver.stop()
        logging.info("Joining Mesos driver")
        result = self.driver.join()
        logging.info("Joined Mesos driver")
        if result != mesos_pb2.DRIVER_STOPPED:
            raise RuntimeError("Mesos driver failed with %i", result)

    def join(self):
        self.driver.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


class OneOffExecutor(Executor):

    def on_launch(self, driver, task):
        def run_task():
            driver.update(task.status('TASK_RUNNING'))
            logging.info('Sent TASK_RUNNING status update')

            try:
                logging.info('Executing task...')
                result = task()
            except Exception as e:
                logging.exception('Task errored')
                driver.update(task.status('TASK_FAILED',
                                          data=e,
                                          message=e.message))
                logging.info('Sent TASK_RUNNING status update')
            else:
                driver.update(task.status('TASK_FINISHED', data=result))
                logging.info('Sent TASK_FINISHED status update')

        thread = threading.Thread(target=run_task)
        thread.start()

    def on_kill(self, driver, task_id):
        driver.stop()


if __name__ == '__main__':
    status = Running(OneOffExecutor()).run()
    code = 0 if status == mesos_pb2.DRIVER_STOPPED else 1
    sys.exit(code)
