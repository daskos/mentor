from __future__ import absolute_import, division, print_function

from functools import partial

from ..messages import PythonTask
from ..queue import Queue
from ..scheduler import AsyncResult, QueueScheduler, Running

__all__ = ('Pool',
           'Queue',
           'AsyncResult')


class Pool(Running):

    def __init__(self, processes=-1, *args, **kwargs):
        self.processes = processes
        self.scheduler = QueueScheduler()
        super(Pool, self).__init__(self.scheduler, *args, **kwargs)

    def close(self):
        self.stop()

    def terminate(self):
        self.stop()

    def join(self):
        self.join()

    def wait(self):
        self.scheduler.wait()

    def map(self, func, iterable, chunksize=1):
        results = self.map_async(func, iterable, chunksize)
        for result in results:
            result.wait()
        return [result.get() for result in results]

    def map_async(self, func, iterable, chunksize=1, callback=None):
        return map(partial(self.apply_async, func=func), iterable)  # TODO

    def apply(self, func, args=[], kwds={}):
        result = self.apply_async(func=func, args=args, kwds=kwds)
        result.wait()
        return result.get()

    def apply_async(self, func, args=[], kwds={}, callback=None, **kwargs):
        # TODO: callback
        task = PythonTask(name='multiprocessing-task',
                          fn=func, args=args, kwargs=kwds, **kwargs)

        return self.scheduler.submit(task)
