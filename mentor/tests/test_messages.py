from __future__ import absolute_import, division, print_function

import pytest
from mentor.messages import ( TaskInfo,Offer,ResourceMixin,Message,Cpus,Mem,Disk)

import json
@pytest.fixture
def d():
    return {'a': 1,
            'b': [{'j': 9},
                  {'g': 7, 'h': 8}],
            'c': {'d': 4,
                  'e': {'f': 6}}}


def test_task_info_resources():
    task = TaskInfo(name='test-task',
                    task_id=Message(value='test-task-id'),
                    resources=[Cpus(0.1), Mem(16)],)
    pb = task
    assert pb.name == 'test-task'
    assert pb.task_id.value == 'test-task-id'
    assert pb.resources[0].name == 'cpus'
    assert pb.resources[0].scalar.value == 0.1
    assert pb.resources[1].name == 'mem'
    assert pb.resources[1].scalar.value == 16





def test_resources_mixin_comparison():
    o1 = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    o2 = Offer(resources=[Cpus(2), Mem(256), Disk(1024)])

    t1 = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])
    t2 = TaskInfo(resources=[Cpus(1), Mem(256), Disk(512)])
    t3 = TaskInfo(resources=[Cpus(0.5), Mem(256), Disk(512)])

    assert o1.cpus.scalar.value == 1
    assert o1.mem.scalar.value == 128
    assert o2.cpus.scalar.value == 2
    assert o2.disk.scalar.value == 1024

    assert t1.cpus.scalar.value == 0.5
    assert t1.mem.scalar.value == 128
    assert t2.cpus.scalar.value == 1
    assert t2.disk.scalar.value == 512

    assert o1 == o1
    assert o1 < o2
    assert o1 <= o2
    assert o2 > o1
    assert o2 >= o1

    assert t1 == t1
    assert t1 < t2
    assert t1 <= t2
    assert t2 > t1
    assert t2 >= t1

    assert o1 >= t1
    assert o2 >= t1
    assert o2 >= t2
    assert t2 >= o1

    assert t3 > o1
    assert t3 <= t2
    assert t3 > t1


def test_resources_mixin_addition():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

    s = o + t
    assert isinstance(s, ResourceMixin)
    assert s.cpus == Cpus(1.5)
    assert s.cpus.scalar.value == 1.5
    assert s.mem == Mem(256)
    assert s.mem.scalar.value == 256
    assert s.disk == Disk(0)
    assert s.disk.scalar.value == 0


def test_resources_mixin_sum():
    o1 = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    o2 = Offer(resources=[Cpus(2), Mem(128), Disk(100)])
    o3 = Offer(resources=[Cpus(0.5), Mem(256), Disk(200)])

    s = sum([o1, o2, o3])
    assert isinstance(s, ResourceMixin)
    assert s.cpus == Cpus(3.5)
    assert s.cpus.scalar.value == 3.5
    assert s.mem == Mem(512)
    assert s.mem.scalar.value == 512
    assert s.disk == Disk(300)
    assert s.disk.scalar.value == 300


def test_resources_mixin_subtraction():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

    s = o - t
    assert isinstance(s, ResourceMixin)
    assert s.cpus == Cpus(0.5)
    assert s.cpus.scalar.value == 0.5
    assert s.mem == Mem(0)
    assert s.mem.scalar.value == 0
    assert s.disk == Disk(0)
    assert s.disk.scalar.value == 0


def test_resources_mixin_inplace_addition():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(64)])
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

    o += t
    assert isinstance(o, Offer)
    assert o.cpus == Cpus(1.5)
    assert o.cpus.scalar.value == 1.5
    assert o.mem == Mem(256)
    assert o.mem.scalar.value == 256
    assert o.disk == Disk(64)
    assert o.disk.scalar.value == 64


def test_resources_mixin_inplace_subtraction():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(64)])
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

    o -= t
    assert isinstance(o, Offer)
    assert o.cpus == Cpus(0.5)
    assert o.cpus.scalar.value == 0.5
    assert o.mem == Mem(0)
    assert o.mem.scalar.value == 0
    assert o.disk == Disk(64)
    assert o.disk.scalar.value == 64




def test_encode_task_info():
    t = TaskInfo(name='test-task',
                 task_id=Message(value='test-task-id'),
                 resources=[Cpus(0.1), Mem(16)],
                 command=Message(value='echo 100'))

    p = t
    assert isinstance(p, TaskInfo)
    assert p.command.value == 'echo 100'
    assert p.name == 'test-task'
    assert p.resources[0].name == 'cpus'
    assert p.resources[0].scalar.value == 0.1
    assert p.task_id.value == 'test-task-id'


def test_json():
    o1 = Offer(resources=[Cpus(1), Mem(128), Disk(0)])

    t1 = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

    assert o1 == Offer(json.loads(json.dumps(o1)))
    assert t1 == TaskInfo(json.loads(json.dumps(t1)))