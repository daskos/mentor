import time

import pytest
from satyr.apis.multiprocessing import AsyncResult, Pool


def test_apply_async():
    with Pool(name='test-pool') as pool:
        res1 = pool.apply_async(lambda a, b: a + b, [1, 2])
        res2 = pool.apply_async(lambda a, b: a * b, [3, 5])
        pool.scheduler.wait()

        assert isinstance(res1, AsyncResult)
        assert isinstance(res2, AsyncResult)

        assert res1.get(timeout=5) == 3
        assert res2.get(timeout=5) == 15


def test_multiple_apply_async():
    with Pool(name='test-pool') as pool:
        # launching multiple evaluations asynchronously *may* use more
        # processes
        results = [pool.apply_async(lambda a, b: a + b, [1, i])
                   for i in range(4)]
        values = [res.get(timeout=5) for res in results]
        expected = [i + 1 for i in range(4)]
        assert values == expected


# def test_queue_apply_async(sched):
#     # launching multiple evaluations asynchronously *may* use more processes
#     queue = Queue()
#     results = [sched.apply_async(feed, [i, queue]) for i in range(4)]
#     values = [res.get(timeout=5) for res in results]

#     assert queue.get() == 1
#     assert queue.get() == 2


# def test_apply_async_timeout(sched):
#     with pytest.raises(TimeoutError):
#         res = pool.apply_async(time.sleep, (10,))
#         res.get(timeout=1)
