from __future__ import absolute_import, division, print_function

import time

# TODO: change thrown errors to these
from concurrent.futures import ALL_COMPLETED, CancelledError, TimeoutError

from ..messages import PythonTask
from ..scheduler import QueueScheduler, Running
from ..utils import timeout as seconds

__all__ = ('MesosPoolExecutor',
           'Future')


def wait(fs, timeout=None, return_when=ALL_COMPLETED):
    raise NotImplementedError()


def as_completed(fs, timeout=None):
    raise NotImplementedError()


class Future(object):

    def __init__(self, task):
        self.task = task

    @property
    def status(self):
        return self.task.status

    def cancel(self):
        raise NotImplementedError()

    def cancelled(self):
        return self.status.has_killed()

    def running(self):
        return (self.status.is_running() or
                self.status.is_starting() or
                self.status.is_staging())

    def done(self):
        return self.status.has_killed() or self.status.has_finished()

    def result(self, timeout=None):
        with seconds(timeout):
            while not self.status.has_terminated():
                time.sleep(0.1)
            if self.status.has_finished():
                return self.status.data
            else:
                raise self.status.data

    def exception(self, timeout=None):
        with seconds(timeout):
            while not self.status.has_terminated():
                time.sleep(0.1)
            if self.status.has_finished():
                return None
            else:
                return self.status.data

    def add_done_callback(self, fn):
        raise NotImplementedError()


class MesosPoolExecutor(Running):

    def __init__(self, max_workers=-1, *args, **kwargs):
        self.max_worker = max_workers  # TODO
        self.scheduler = QueueScheduler()
        super(MesosPoolExecutor, self).__init__(
            self.scheduler, *args, **kwargs)

    def submit(self, fn, args=[], kwargs={}, **kwds):
        task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                          name=kwds.pop('name', 'futures'), **kwds)
        self.scheduler.submit(task)
        return Future(task)

    def map(self, func, *iterables, **kwargs):
        timeout = kwargs.pop('timeout', None)
        chunksize = kwargs.pop('chunksize', 1)
        for item in zip(*iterables):
            future = self.submit(func, args=item, **kwargs)
            yield future.result(timeout=timeout)

    def shutdown(self, wait=True):
        if wait:
            self.scheduler.wait(-1)
        self.stop()
