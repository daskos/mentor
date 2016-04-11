import pytest
from satyr.multiprocessing import AsyncResult, apply_async


def add(a, b):
    return a + b


def mul(a, b):
    return a * b


def feed(x, queue):
    queue.put(x)


@pytest.fixture
def sched():
    return Satyr(config)


def test_apply_async(sched):
    res1 = sched.apply_async(add, [1, 2])
    res2 = sched.apply_async(mul, [3, 5])

    assert isinstance(res1, AsyncResult)
    assert isinstance(res2, AsyncResult)
    assert res1.get(timeout=5) == 2
    assert res2.get(timeout=5) == 15


def test_multiple_apply_async(sched):
    # launching multiple evaluations asynchronously *may* use more processes
    results = [sched.apply_async(add, [1, i]) for i in range(4)]
    values = [res.get(timeout=5) for res in results]
    expected = [i + 1 for i in range(4)]
    assert values == expected


def test_queue_apply_async(sched):
    # launching multiple evaluations asynchronously *may* use more processes
    queue = Queue()
    results = [sched.apply_async(feed, [i, queue]) for i in range(4)]
    values = [res.get(timeout=5) for res in results]

    assert queue.get() == 1
    assert queue.get() == 2


def test_apply_async_timeout(sched):
    with pytest.raises(TimeoutError):
        res = pool.apply_async(time.sleep, (10,))
        res.get(timeout=1)


# # make a single worker sleep for 10 secs

# class FIFOScheduler(BaseScheduler):

#     resourceOffer = ResourceOfferHandler(pina=100)
#     statusUpdate = StatusUpdateHandler()

# FIFO, LIFO, Priority
# BIN_PACKING
# fitness
