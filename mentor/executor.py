from __future__ import absolute_import, division, print_function

import logging
import multiprocessing
import sys
import threading
import traceback
from functools import partial

from mentos.executor import ExecutorDriver
from mentos.interface import Executor
from mentor.messages import  PythonTaskStatus, PythonTask
from mentor.utils import Interruptable

log = logging.getLogger(__name__)


class ThreadExecutor(Executor):

    def __init__(self):
        self.tasks = {}

    def is_idle(self):
        return not len(self.tasks)

    def run(self, driver, task):

        status = PythonTaskStatus(task_id=task.task_id, state='TASK_RUNNING')
        driver.update(status)
        log.info('Sent TASK_RUNNING status update')
        try:
            log.info('Executing task...')
            result = task()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = ''.join(traceback.format_tb(exc_traceback))
            log.exception('Task errored with {}'.format(e))
            status = PythonTaskStatus(
                task_id=task.task_id, state='TASK_FAILED', data=(tb, e), message=repr(e))
            driver.update(status)
            log.info('Sent TASK_RUNNING status update')
        else:
            status = PythonTaskStatus(
                task_id=task.task_id, state='TASK_FINISHED', data=result)
            driver.update(status)
            log.info('Sent TASK_FINISHED status update')
        finally:
            del self.tasks[task.task_id.value]
            if self.is_idle():  # no more tasks left
                log.info('Executor stops due to no more executing '
                         'tasks left')
                driver.stop()

    def on_launch(self, driver, task):
        log.info("Stuff")
        log.info(task)
        task = PythonTask(**task)
        thread = threading.Thread(target=self.run, args=(driver, task))
        # track tasks runned by this executor
        self.tasks[task.task_id.value] = thread
        thread.start()

    def on_kill(self, driver, task_id):
        driver.stop()

    def on_shutdown(self, driver):
        driver.stop()

    def on_outbound_success(self, driver, request):
            pass

    def on_outbound_error(self,  driver, request, endpoint, error):
            pass

class ProcessExecutor(ThreadExecutor):

    def on_launch(self, driver, task):
        log.info("Stuff")
        log.info(task)
        task = PythonTask(**task)
        process = multiprocessing.Process(target=self.run, args=(driver, task))
        # track tasks runned by this executor
        self.tasks[task.task_id] = process
        process.start()

    def on_kill(self, driver, task_id):

        self.tasks[task_id].terminate()
        del self.tasks[task_id]

        if self.is_idle():  # no more tasks left
            log.info('Executor stops due to no more executing '
                     'tasks left')
            driver.stop()

    def on_outbound_success(self, driver, event):
        pass

    def on_outbound_error(self, driver, event):
        pass

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    driver = ExecutorDriver(ThreadExecutor())
    driver.start(block=True)
