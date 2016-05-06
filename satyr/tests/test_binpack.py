from __future__ import absolute_import, division, print_function

import pytest
from satyr.binpack import bf, bfd, ff, ffd, mr, weight
from satyr.proxies.messages import Cpus, Mem, Offer, TaskInfo


@pytest.fixture
def offers():
    resources = [(1.1, 2048),
                 (2.0, 512),
                 (0.8, 1024),
                 (1.6, 2048)]
    return [Offer(resources=[Cpus(cpus), Mem(mem)])
            for cpus, mem in resources]


@pytest.fixture
def tasks():
    resources = [(0.1, 128),
                 (1.0, 256),
                 (3.0, 4096),
                 (0.2, 64),
                 (1.4, 1024),
                 (0.5, 128),
                 (0.1, 128)]

    return [TaskInfo(resources=[Cpus(cpus), Mem(mem)])
            for cpus, mem in resources]


def test_weight(offers):
    assert round(sum(weight(offers, cpus=1)), 1) == 1.0
    assert round(sum(weight(offers, cpus=1, mem=1)), 1) == 2.0
    assert round(sum(weight(offers, cpus=4, mem=1.5)), 1) == 5.5


def test_ff(tasks, offers):
    bins, skip = ff(tasks, offers)
    assert skip == [tasks[2]]


def test_ffd(tasks, offers):
    bins, skip = ffd(tasks, offers, cpus=1, mem=1)
    assert skip == [tasks[2]]


def test_mr(tasks, offers):
    bins, skip = mr(tasks, offers, cpus=1, mem=1)
    assert skip == [tasks[2], tasks[4]]


def test_bf(tasks, offers):
    bins, skip = bf(tasks, offers, cpus=1, mem=1)
    assert skip == [tasks[2]]


def test_bfd(tasks, offers):
    bins, skip = bfd(tasks, offers, cpus=1, mem=1)
    assert skip == [tasks[2]]
