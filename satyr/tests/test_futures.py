from __future__ import absolute_import, division, print_function

import operator
import time
from collections import Iterator

import pytest
from satyr.apis.futures import Future, MesosPoolExecutor
from satyr.proxies.messages import Cpus, Disk, Mem
from satyr.utils import RemoteException, TimeoutError, timeout


@pytest.fixture
def resources():
    return [Cpus(0.1), Mem(128), Disk(0)]


def test_submit():
    with MesosPoolExecutor(name='futures-pool') as executor:
        future1 = executor.submit(operator.add, [1, 2])
        future2 = executor.submit(operator.mul, [3, 5])

        assert isinstance(future1, Future)
        assert isinstance(future2, Future)

        assert future1.result(timeout=30) == 3
        assert future2.result(timeout=30) == 15


def test_future_states():
    def add(a, b):
        time.sleep(2)
        return a + b

    with MesosPoolExecutor(name='futures-pool') as executor:
        future = executor.submit(add, [1, 2])
        with timeout(30):
            while future.running():
                time.sleep(0.1)
            assert future.running() is False
            assert future.done() is True
            assert future.result() == 3


def test_future_timeout():
    with pytest.raises(TimeoutError):
        with MesosPoolExecutor(name='futures-pool') as executor:
            future1 = executor.submit(time.sleep, [3])
            future1.result(timeout=2)


def test_future_raises_exception(resources):
    def raiser():
        raise ValueError('Boooom!')

    with MesosPoolExecutor(name='futures-pool') as executor:
        with pytest.raises(RemoteException) as e:
            future1 = executor.submit(raiser, resources=resources)
            future1.result(timeout=30)
            assert isinstance(e.value, ValueError)


def test_future_catches_exception(resources):
    def raiser():
        raise TypeError('Boooom!')

    with MesosPoolExecutor(name='futures-pool') as executor:
        future = executor.submit(raiser)
        e = future.exception(timeout=30)
        assert isinstance(e, RemoteException)
        assert isinstance(e, TypeError)


def test_multiple_submit(resources):
    def fn(a, b):
        return a + b

    with MesosPoolExecutor(name='futures-pool') as executor:
        futures = [executor.submit(fn, args=[1, i], resources=resources)
                   for i in range(4)]
        values = [f.result(timeout=30) for f in futures]

    assert values == [i + 1 for i in range(4)]


def test_map(resources):
    with MesosPoolExecutor(name='futures-pool') as executor:
        it = executor.map(operator.add, range(10), range(10),
                          resources=resources)
        assert isinstance(it, Iterator)
        for i, v in enumerate(it):
            assert i + i == v
