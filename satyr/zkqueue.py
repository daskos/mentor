from kazoo.recipe.queue import Queue, LockingQueue


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


class ZkQueue(Queue, SerializeMixin):
    pass

class ZkLockingQueue(LockingQueue, SerializeMixin):
    pass
