from collections import deque

from kazoo.recipe.queue import LockingQueue as KazooLockingQueue
from kazoo.recipe.queue import Queue as KazooQueue


class Queue(deque):

    def put(self, value):
        self.append(value)

    def get(self):
        return self.popleft()

    def empty(self):
        return len(self) == 0


class SerializeMixin(object):

    def __getstate__(self):
        hosts = ["{}:{}".format(h, p) for h, p in self.client.hosts]
        client = ",".join(hosts)

        result = self.__dict__.copy()
        result['client'] = client

        return result

    def __setstate__(self, state):
        hosts = state.pop('client')
        client = KazooClient(hosts)
        client.start()

        self.__dict__ = state
        self.client = client


# class Queue(KazooQueue, SerializeMixin):
#    pass


class LockingQueue(KazooLockingQueue, SerializeMixin):
    pass
