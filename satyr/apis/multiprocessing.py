from __future__ import absolute_import, division, print_function

import time
from Queue import Empty

import cloudpickle

from ..messages import PythonTask
from ..queue import Queue as ZkQueue
from ..scheduler import AsyncResult, QueueScheduler, Running
from ..utils import timeout as seconds
from ..utils import TimeoutError

__all__ = ('Pool',
           'Queue',
           'AsyncResult')


class Queue(ZkQueue):  # multiprocessing compatible queue

    def __bool__(self):
        return True

    def __nonzero__(self):
        return True

    def get(self, block=True, timeout=-1):
        result = super(Queue, self).get()

        if block:
            try:
                with seconds(timeout):
                    while result is None:
                        result = super(Queue, self).get()
                        time.sleep(0.1)
            except TimeoutError:
                raise Empty

        return cloudpickle.loads(result)

    def put(self, item):
        value = cloudpickle.dumps(item)
        return super(Queue, self).put(value)

    def qsize(self):
        return len(self)

    def empty(self):
        return len(self) == 0


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
        task = PythonTask(name=kwargs.pop('name', 'multiprocessing'),
                          fn=func, args=args, kwargs=kwds, **kwargs)

        return self.scheduler.submit(task)
