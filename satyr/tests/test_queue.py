import cloudpickle as cp
import pytest
from satyr.queue import LockingQueue, Queue


def test_queue_put_get(zk):
    queue = Queue(zk, '/satyr/putget')
    queue.put(cp.dumps(range(5)))
    assert cp.loads(queue.get()) == range(5)


def test_locking_queue_put_get(zk):
    queue = LockingQueue(zk, '/satyr/putget_locking')
    queue.put(cp.dumps(range(5)))
    assert queue.get() == cp.dumps(range(5))
    queue.consume()


def test_queue_serde(zk):
    queue = Queue(zk, '/satyr/serde')
    queue.put(cp.dumps({'a': 1, 'b': 2}))
    queue.put(cp.dumps({'c': 3}))

    pickled_queue = cp.dumps(queue)
    unpickled_queue = cp.loads(pickled_queue)

    assert cp.loads(unpickled_queue.get()) == {'a': 1, 'b': 2}
    assert cp.loads(unpickled_queue.get()) == {'c': 3}


def test_locking_queue_serde(zk):
    queue = LockingQueue(zk, '/satyr/serde_locking')
    queue.put(cp.dumps({'a': 1, 'b': 2}))
    queue.put(cp.dumps({'c': 3}))

    pickled_queue = cp.dumps(queue)
    unpickled_queue = cp.loads(pickled_queue)

    assert cp.loads(unpickled_queue.get()) == {'a': 1, 'b': 2}
    unpickled_queue.consume()
    assert cp.loads(unpickled_queue.get()) == {'c': 3}
    unpickled_queue.consume()
