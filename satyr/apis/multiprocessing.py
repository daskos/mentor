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


class Pool(BaseScheduler):

    def __init__(self, processes=-1, *args, **kwargs):
        self.processes = processes
        super(Pool, self).__init__(*args, **kwargs)
        self.daemonize()

    def close(self):
        pass

    def terminate(self):
        pass

    def join(self):
        pass

    def map(self, func, iterable, chunksize=1):
        results = self.map_async(func, iterable, chunksize, callback)
        if callback_finished:  # indicating computation finished on all elements
            # block until completion
            return results

    def map_async(self, func, iterable, chunksize=1, callback=None):
        return map(partial(self.apply_async, func=func), iterable)  # TODO

    def apply(self, func, args=[], kwds={}):
        pass

    def apply_async(self, func, args=[], kwds={}, callback=None, **kwargs):
        task = PythonTask(fn=func, args=args, kwargs=kwds, on_success=callback,
                          **kwargs)

        return self.submit(task)
