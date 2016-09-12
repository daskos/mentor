from __future__ import absolute_import, division, print_function

import time
from Queue import Empty

import cloudpickle as cp
from kazoo.client import KazooClient
from kazoo.recipe.queue import LockingQueue as KazooLockingQueue
from kazoo.recipe.queue import Queue as KazooQueue

from .utils import timeout as seconds
from .utils import TimeoutError


class SerializableMixin(object):

    @staticmethod
    def init(cls, hosts, path):
        client = KazooClient(hosts=hosts)
        client.start()
        return cls(client, path)

    def __reduce__(self):
        hosts = ",".join(["{}:{}".format(h, p) for h, p in self.client.hosts])
        return (SerializableMixin.init, (self.__class__, hosts, self.path))


class CompatMixin(object):  # Python's Queue compatibility

    def __bool__(self):
        return True

    def __nonzero__(self):
        return True

    def qsize(self):
        return len(self)

    def empty(self):
        return len(self) == 0


class Queue(CompatMixin, SerializableMixin, KazooQueue):

    def get(self, block=True, timeout=-1):
        result = super(Queue, self).get()

        if block:
            try:
                with seconds(timeout):
                    while result is None:
                        result = super(Queue, self).get()
                        time.sleep(0.001)
            except TimeoutError:
                raise Empty

        return cp.loads(result)

    def put(self, item):
        value = cp.dumps(item)
        return super(Queue, self).put(value)


class LockingQueue(CompatMixin, SerializableMixin, KazooLockingQueue):

    def get(self, block=True, timeout=-1):
        result = super(LockingQueue, self).get(timeout=timeout)
        return cp.loads(result)

    def put(self, item, priority=100):
        value = cp.dumps(item)
        return super(LockingQueue, self).put(value, priority=priority)
