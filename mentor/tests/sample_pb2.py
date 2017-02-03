from __future__ import absolute_import, division, print_function

import pytest
from mentor.messages import ( TaskInfo,Offer,ResourceMixin)

import json
@pytest.fixture
def d():
    return {'a': 1,
            'b': [{'j': 9},
                  {'g': 7, 'h': 8}],
            'c': {'d': 4,
                  'e': {'f': 6}}}


def cpus():
    return {'name': 'cpus', 'role': '*', 'scalar': {'value': 0.1}, 'type': 'SCALAR'}

def mem():
    return {'name': 'mem', 'role': '*', 'scalar': {'value': 16}, 'type': 'SCALAR'}

def disk():
    return {'name': 'disk', 'role': '*', 'scalar': {'value': 100}, 'type': 'SCALAR'}

def test_task_info_resources(cpus,mem):
    task = TaskInfo.encode(dict(name='test-task',
                    task_id=dict(value='test-task-id'),
                    resources=[cpus,mem],))
    pb = task
    assert pb.name == 'test-task'
    assert pb.task_id.value == 'test-task-id'
    assert pb.resources[0].name == 'cpus'
    assert pb.resources[0].scalar.value == 0.1
    assert pb.resources[1].name == 'mem'
    assert pb.resources[1].scalar.value == 16





def test_resources_mixin_comparison(cpus,mem,disk):
    o1 = Offer(resources=[cpus,mem,disk])
    o2 = Offer(resources=[cpus,mem,disk])

    t1 = TaskInfo(resources=[cpus,mem,disk])
    t2 = TaskInfo(resources=[cpus,mem,disk])
    t3 = TaskInfo(resources=[cpus,mem,disk])

    assert o1.cpus == 1
    assert o1.mem == 128
    assert o2.cpus == 2
    assert o2.disk == 1024

    assert t1.cpus == 0.5
    assert t1.mem == 128
    assert t2.cpus == 1
    assert t2.disk == 512

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


def test_resources_mixin_addition(cpus,mem,disk):
    o = Offer(resources=[cpus,mem,disk])
    t = TaskInfo.encode(dict(resources=[cpus,mem,disk]))

    s = o + t
    assert isinstance(s, ResourceMixin)
    assert s.cpus == cpus
    assert s.cpus == 1.5
    assert s.mem == mem
    assert s.mem == 256
    assert s.disk == disk
    assert s.disk == 0


def test_resources_mixin_sum():
    o1 = Offer(resources=[cpus,mem,disk])
    o2 = Offer(resources=[cpus,mem,disk])
    o3 = Offer(resources=[cpus,mem,disk])

    s = sum([o1, o2, o3])
    assert isinstance(s, ResourceMixin)
    assert s.cpus == cpus
    assert s.cpus == 3.5
    assert s.mem == mem
    assert s.mem == 512
    assert s.disk == disk
    assert s.disk == 300


def test_resources_mixin_subtraction():
    o = Offer(resources=[cpus,mem,disk])
    t = TaskInfo(resources=[cpus,mem,disk])

    s = o - t
    assert isinstance(s, ResourceMixin)
    assert s.cpus == cpus
    assert s.cpus == 0.5
    assert s.mem == mem
    assert s.mem == 0
    assert s.disk == disk
    assert s.disk == 0


def test_resources_mixin_inplace_addition(cpus,mem,disk):
    o = Offer(resources=[cpus,mem,disk])
    t = TaskInfo.encode(dict(resources=[cpus,mem,disk]))

    o += t
    assert isinstance(o, Offer)
    assert o.cpus == cpus
    assert o.cpus == 1.5
    assert o.mem == mem
    assert o.mem == 256
    assert o.disk == disk
    assert o.disk == 64


def test_resources_mixin_inplace_subtraction():
    o = Offer(resources=[cpus,mem,disk])
    t = TaskInfo.encode(dict(resources=[cpus,mem,disk]))

    o -= t
    assert isinstance(o, Offer)
    assert o.cpus == cpus
    assert o.cpus == 0.5
    assert o.mem == mem
    assert o.mem == 0
    assert o.disk == disk
    assert o.disk == 64
 

def test_encode_task_info(cpus,mem,disk):
    t = TaskInfo.encode(dict(name='test-task',
                 task_id=dict(value='test-task-id'),
                 resources=[cpus,mem,disk],
                 command=dict(value='echo 100')))

    p = t
    assert isinstance(p, TaskInfo)
    assert p.command.value == 'echo 100'
    assert p.name == 'test-task'
    assert p.resources[0].name == 'cpus'
    assert p.resources[0].scalar.value == 0.1
    assert p.task_id.value == 'test-task-id'


 
def test_json(cpus,mem,disk):
    o1 = Offer(resources=[cpus,mem,disk])

    t1 = TaskInfo(resources=[cpus,mem,disk])

    assert o1 == Offer.encode(json.loads(json.dumps(o1)))
    assert t1 == TaskInfo.encode(json.loads(json.dumps(t1)))