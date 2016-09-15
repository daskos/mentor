from __future__ import absolute_import, division, print_function

import logging
import multiprocessing
import sys
import threading
import traceback
from functools import partial

from mesos.interface import mesos_pb2
from mesos.native import MesosExecutorDriver

from .interface import Executor
from .messages import PythonTaskStatus
from .proxies import ExecutorDriverProxy, ExecutorProxy
from .utils import Interruptable


class ExecutorDriver(ExecutorDriverProxy, Interruptable):

    def __init__(self, executor):
        executor = ExecutorProxy(executor)
        driver = MesosExecutorDriver(executor)
        super(ExecutorDriver, self).__init__(driver)


class ThreadExecutor(Executor):

    def __init__(self):
        self.tasks = {}

    def is_idle(self):
        return not len(self.tasks)

    def run(self, driver, task):
        status = partial(PythonTaskStatus, task_id=task.id)
        driver.update(status(state='TASK_RUNNING'))
        logging.info('Sent TASK_RUNNING status update')

        try:
            logging.info('Executing task...')
            result = task()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = ''.join(traceback.format_tb(exc_traceback))
            logging.exception('Task errored with {}'.format(e))
            driver.update(status(state='TASK_FAILED',
                                 data=(e, tb),
                                 message=e.message))
            logging.info('Sent TASK_RUNNING status update')
        else:
            driver.update(status(state='TASK_FINISHED', data=result))
            logging.info('Sent TASK_FINISHED status update')
        finally:
            del self.tasks[task.id]
            if self.is_idle():  # no more tasks left
                logging.info('Executor stops due to no more executing '
                             'tasks left')
                driver.stop()

    def on_launch(self, driver, task):
        thread = threading.Thread(target=self.run, args=(driver, task))
        self.tasks[task.id] = thread  # track tasks runned by this executor
        thread.start()

    def on_kill(self, driver, task_id):
        driver.stop()

    def on_shutdown(self, driver):
        driver.stop()


class ProcessExecutor(ThreadExecutor):

    def on_launch(self, driver, task):
        process = multiprocessing.Process(target=self.run, args=(driver, task))
        self.tasks[task.id] = process  # track tasks runned by this executor
        process.start()

    def on_kill(self, driver, task_id):
        self.tasks[task_id].terminate()
        del self.tasks[task_id]

        if self.is_idle():  # no more tasks left
            logging.info('Executor stops due to no more executing '
                         'tasks left')
            driver.stop()


if __name__ == '__main__':
    status = ExecutorDriver(ThreadExecutor()).run()
    code = 0 if status == mesos_pb2.DRIVER_STOPPED else 1
    sys.exit(code)
