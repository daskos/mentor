from __future__ import absolute_import, division, print_function

import threading
from Queue import Empty

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


def test_queue_size(zk):
    queue = Queue(zk, '/satyr/size')
    assert queue.empty()
    assert queue.qsize() == 0

    queue.put(cp.dumps(range(5)))
    assert queue.empty() is False
    assert queue.qsize() == 1


def test_queue_blocking_get(zk):
    queue = Queue(zk, '/satyr/blocking')

    def delayed_put():
        import time
        time.sleep(2)
        queue.put(cp.dumps(range(5)))

    t = threading.Thread(target=delayed_put)
    t.start()
    with pytest.raises(Empty):
        queue.get(block=True, timeout=1)

    assert queue.get(block=True, timeout=2) == cp.dumps(range(5))
