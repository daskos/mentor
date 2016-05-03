import time

import cloudpickle as cp
import pytest
from satyr.apis.multiprocessing import AsyncResult, Pool, Queue
from satyr.utils import TimeoutError


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
            res = pool.apply_async(time.sleep, (10,))
            res.get(timeout=1)


def test_apply():
    with Pool(name='test-pool') as pool:
        result = pool.apply(lambda a, b: a + b, [1, 3])
        assert result == 4

        result = pool.apply(lambda a, b: a + b, ['a', 'b'])
        assert result == 'ab'


def test_multiple_apply_async():
    with Pool(name='test-pool') as pool:
        results = [pool.apply_async(lambda a, b: a + b, [1, i])
                   for i in range(5)]
        values = [res.get(timeout=10) for res in results]
        expected = [i + 1 for i in range(5)]
        assert values == expected


def test_queue_apply_async(zk):
    def feed(i, queue):
        queue.put(cp.dumps(i))

    queue = Queue(zk, '/satyr/test-pool')
    with Pool(name='test-pool') as pool:
        results = [pool.apply_async(feed, [i, queue]) for i in range(4)]
        pool.wait()

    results = [cp.loads(queue.get()) for i in range(4)]
    assert sorted(results) == range(4)


def test_map_async():
    with Pool(name='test-pool') as pool:
        results = pool.map_async(
            lambda tpl: tpl[0] + tpl[1], zip(range(5), range(5)))
        assert all([isinstance(res, AsyncResult) for res in results])

        values = [res.get(timeout=10) for res in results]
        expected = [i + i for i in range(5)]
        assert values == expected


def test_map():
    with Pool(name='test-pool') as pool:
        results = pool.map(
            lambda tpl: tpl[0] + tpl[1], zip(range(5), range(5)))
        expected = [i + i for i in range(5)]
        assert results == expected
