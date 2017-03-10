from __future__ import absolute_import, division, print_function

import time

import cloudpickle as cp
import pytest
from mentor.apis.multiprocessing import AsyncResult, Pool, Queue
from mentor.messages.base import Cpus, Disk, Mem
from mentor.utils import TimeoutError


@pytest.fixture
def resources():
    return [Cpus(0.1), Mem(128), Disk(0)]


def test_apply_async():
    with Pool(name='test-pool') as pool:
        res1 = pool.apply_async(lambda a, b: a + b, [1, 2])
        res2 = pool.apply_async(lambda a, b: a * b, [3, 5])
        pool.wait()

        assert isinstance(res1, AsyncResult)
        assert isinstance(res2, AsyncResult)

        assert res1.get(timeout=10) == 3
        assert res2.get(timeout=10) == 15


def test_apply_async_timeout():
    with pytest.raises(TimeoutError):
        with Pool(name='test-pool') as pool:
            res = pool.apply_async(time.sleep, (3,))
            res.get(timeout=1)


def test_apply():
    with Pool(name='test-pool') as pool:
        result = pool.apply(lambda a, b: a + b, [1, 3])
        assert result == 4

        result = pool.apply(lambda a, b: a + b, ['a', 'b'])
        assert result == 'ab'
        pool.wait(seconds=20)


def test_multiple_apply_async(resources):
    def fn(a, b):
        return a + b

    with Pool(name='test-pool') as pool:
        results = [pool.apply_async(fn, [1, i],
                                    resources=resources)
                   for i in range(4)]
        values = [res.get(timeout=30) for res in results]

    assert values == [i + 1 for i in range(4)]


@pytest.mark.skip(reason='Some wierd kazoo connection issue')
def test_queue_apply_async(zk, resources):
    def feed(i, queue):
        queue.put(cp.dumps(i))

    queue = Queue(zk, '/mentor/test-pool')
    with Pool(name='test-pool') as pool:
        results = [pool.apply_async(feed, [i, queue], resources=resources)
                   for i in range(4)]
        pool.wait(seconds=30)

    time.sleep(1)
    results = [cp.loads(queue.get()) for i in range(4)]
    assert sorted(results) == range(4)


def test_map_async(resources):
    with Pool(name='test-pool') as pool:
        results = pool.map_async(
            lambda tpl: tpl[0] + tpl[1], zip(range(3), range(3)),
            resources=resources)
        assert all([isinstance(res, AsyncResult) for res in results])
        values = [res.get(timeout=60) for res in results]

    assert values == [i + i for i in range(3)]


def test_map(resources):
    with Pool(name='test-pool') as pool:
        results = pool.map(
            lambda tpl: tpl[0] + tpl[1], zip(range(3), range(3)),
            resources=resources)

    expected = [i + i for i in range(3)]
    assert results == expected
