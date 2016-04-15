from __future__ import absolute_import, division, print_function

import copy
import uuid
from collections import deque
from multiprocessing import Queue, TimeoutError
from multiprocessing.pool import AsyncResult
from time import sleep

import cloudpickle

from ..messages import PythonTask
from ..scheduler import BaseScheduler
from ..utils import run_daemon


# class Process(TaskInfo):

#     def __init__(self, target, name=None, args=[], kwargs={})
#         self.name = name
#         self.daemon = False
#         self.pid = None

#     def terminate(self):
#         pass

#     def run(self):
#         pass

#     def start(self):
#         # create single task scheduler and submit task itself
#         pass

#     def join(timeout=None):
#         pass

#     def is_alive(self):
#         pass


# class SatyrAsyncResult(AsyncResult):
#     FLAG_READY = 0
#     FLAG_SUCCESSFUL = 1

#     def __init__(self, satyr, task):
#         self.satyr = satyr
#         self.task = copy.copy(task)
#         self.flags = ()

#     def get(self, timeout=None):
#         self.wait(timeout)
#         return self.satyr.results.get(self.task['id'], None)

#     def wait(self, timeout=None):
#         while not self.ready():
#             sleep(1)
#             print('[%s] Waiting to get ready...' % self.task['id'])

#     def ready(self):
#         return self.FLAG_READY in self.flags

#     def successful(self):
# return self.FLAG_READY in self.flags and self.FLAG_SUCCESSFUL in
# self.flags

#     def update_status(self, task, is_successful):
#         if not self.task['id'] == task.task_id.value:
#             return
#         self.flags = self.flags + \
#             (self.FLAG_SUCCESSFUL,) if is_successful else self.flags


class AsyncResult(object):

    def __init__(self):
        self.value = None

    def get(self, timeout=None):
        pass

    def wait(self, timeout=None):
        pass

    def ready(self):
        pass

    def successful(self):
        pass


class Pool(BaseScheduler):

    def __init__(self, processes=-1, *args, **kwargs):
        self.processes = processes
        self.tasks = deque()
        self.results = {}
        self.callbacks = {}
        super(Pool, self).__init__(*args, **kwargs)
        run_daemon('Mesos Multiprocessing Pool Scheduler', self)

    def close(self):
        pass

    def terminate(self):
        pass

    def join(self):
        pass

    def on_offers(self, driver, offers):
        # max paralellism determined by self.processes
        try:
            task = self.tasks.pop()
        except:
            pass
        else:
            launched = False
            for offer in offers:
                if offer > task:
                    task.slave_id = offer.slave_id
                    driver.launch(offer.id, [task])
                    launched = True
                else:
                    driver.decline(offer.id)
            if not launched:
                self.tasks.append(task)

    def on_update(self, driver, status):
        def pop(task_id):
            result = self.results.pop(status.task_id.value, None)
            callback = self.callbacks.pop(status.task_id.value, None)
            return result, callback

        if status.state == 'TASK_FINISHED':
            result, callback = pop(status.task_id.value)
            result.value = status.data
            if callback:
                callback()
        elif status.state in ['TASK_FAILED', 'TASK_LOST', 'TASK_KILLED']:
            result, callback = pop(status.task_id.value)

        if len(self.tasks) == 0 and len(self.results) == 0:
            driver.stop()

    def map(self, func, iterable, chunksize=1):
        pass

    def map_async(self, func, iterable, chunksize=1, callback=None):
        pass

    def apply(self, func, args=[], kwds={}):
        pass

    def apply_async(self, func, args=[], kwds={}, callback=None, **kwargs):
        task = PythonTask(fn=func, args=args, kwargs=kwds, **kwargs)

        self.tasks.append(task)
        self.callbacks[task.id.value] = callback

        self.results[task.id.value] = AsyncResult()
        return self.results[task.id.value]
