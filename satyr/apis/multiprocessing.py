from __future__ import absolute_import, division, print_function

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
        # TODO: callback
        task = PythonTask(name='multiprocessing-task',
                          fn=func, args=args, kwargs=kwds, **kwargs)

        return self.scheduler.submit(task)
