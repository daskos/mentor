from __future__ import absolute_import, division, print_function

import time

from ..messages import PythonTask
from ..queue import Queue
from ..scheduler import QueueScheduler, Running
from ..utils import timeout

__all__ = ('Pool',
           'Queue',
           'AsyncResult')


class AsyncResult(object):

    def __init__(self, task):
        self.task = task

    @property
    def status(self):
        return self.task.status

    def get(self, timeout=60):
        self.wait(timeout)
        if self.successful():
            return self.status.data
        else:
            try:
                raise self.status.data
            except TypeError:
                raise ValueError('Async result indicate task failed!')

    def wait(self, seconds=60):
        with timeout(seconds):
            while not self.ready():
                time.sleep(0.1)

    def ready(self):
        return self.status.has_terminated()

    def successful(self):
        return self.status.has_succeeded()


class Pool(Running):

    def __init__(self, processes=-1, *args, **kwargs):
        self.processes = processes
        self.scheduler = QueueScheduler()
        super(Pool, self).__init__(self.scheduler, *args, **kwargs)

    def close(self):
        self.stop()

    def terminate(self):
        self.stop()

    def wait(self, seconds=-1):
        self.scheduler.wait(seconds)

    def map(self, func, iterable, chunksize=1, **kwargs):
        results = self.map_async(func, iterable, chunksize, **kwargs)
        return [result.get(timeout=-1) for result in results]

    def map_async(self, func, iterable, chunksize=1, callback=None, **kwargs):
        return [self.apply_async(func, (item,), **kwargs) for item in iterable]

    def apply(self, func, args=[], kwds={}, **kwargs):
        result = self.apply_async(func=func, args=args, kwds=kwds, **kwargs)
        return result.get(timeout=-1)

    def apply_async(self, func, args=[], kwds={}, callback=None, **kwargs):
        task = PythonTask(name=kwargs.pop('name', 'multiprocessing'),
                          fn=func, args=args, kwargs=kwds, **kwargs)
        self.scheduler.submit(task)
        return AsyncResult(task)
