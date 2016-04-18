from __future__ import absolute_import, division, print_function

import atexit
import os
import time
from collections import deque
from uuid import uuid4

from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver

from . import log as logging
from .interface import Scheduler
from .messages import PythonTask, PythonTaskStatus
from .proxies import SchedulerProxy
from .proxies.messages import (FrameworkInfo, ResourcesMixin, TaskID, TaskInfo,
                               encode)


class PackError(Exception):
    pass


class AsyncResult(object):

    def __init__(self, state):
        self.state = state
        self.value = None

    def get(self, timeout=None):
        if self.ready():
            return self.value
        else:
            raise ValueError('Async result not ready!')

    def wait(self, timeout=None):
        while not self.ready():
            time.sleep(0.1)

    def ready(self):
        return self.state not in ['TASK_STAGING', 'TASK_RUNNING']

    def successful(self):
        return self.state in ['TASK_FINISHED']


class BaseScheduler(Scheduler):

    # TODO envargs
    def __init__(self, name, user='', master=os.getenv('MESOS_MASTER'),
                 *args, **kwargs):
        self.framework = FrameworkInfo(name=name, user=user, **kwargs)
        self.master = master
        self.tasks = deque()
        self.results = {}

    def __call__(self):
        return self.run()

    def run(self):
        # TODO logging
        # TODO implicit aknoladgements
        implicit_acknowledge = 1

        driver = MesosSchedulerDriver(SchedulerProxy(self),
                                      encode(self.framework),
                                      self.master,
                                      implicit_acknowledge)
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        return status

    def submit(self, task):  # support commandtask, pythontask etc.
        assert isinstance(task, TaskInfo)
        self.tasks.append(task)
        self.results[task.task_id.value] = AsyncResult('TASK_STAGING')
        return self.results[task.task_id.value]

    # def submit(self, fn, args=[], kwargs={}, **kwds):
    #     tid = kwds.pop('id', None) or TaskID(value=str(uuid4()))
    #     task =
    #     self.tasks.append(task)
    #     self.results[task.id.value] = AsyncResult(task.state)
    #     return self.results[task.id.value]

    def on_offers(self, driver, offers):  # default binpacking
        def pack(task, offers):
            for offer in offers:
                if offer >= task:
                    task.slave_id = offer.slave_id
                    return (offer, task)
            raise PackError('Couldn\'t pack')

        try:
            task = self.tasks.pop()
            offer, task = pack(task, offers)
        except PackError as e:
            self.tasks.append(task)
        except IndexError as e:
            # log empty queue
            pass
        else:
            offers.pop(offers.index(offer))
            driver.launch(offer.id, [task])
        finally:
            for offer in offers:
                driver.decline(offer.id)

    def on_update(self, driver, status):
        result = self.results[status.task_id.value]
        result.state = status.state

        if status.state == 'TASK_FINISHED':
            if isinstance(status, PythonTaskStatus):
                result.value = status.result
            self.results.pop(status.task_id.value)
        elif status.state in ['TASK_FAILED', 'TASK_LOST', 'TASK_KILLED']:
            self.results.pop(status.task_id.value)

        if len(self.tasks) == 0 and len(self.results) == 0:
            driver.stop()


if __name__ == '__main__':
    from .utils import run_daemon

    scheduler = BaseScheduler(name='Base')
    run_daemon('Scheduler Process', scheduler)
