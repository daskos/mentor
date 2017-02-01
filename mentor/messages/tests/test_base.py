from __future__ import absolute_import, division, print_function

import pytest
from mentor.messages.base import ( Cpus, Disk, TaskInfo,
                                   Mem, ScalarResource, ResourcesMixin,TaskStatus,
                                  Offer)

import json
@pytest.fixture
def d():
    return {'a': 1,
            'b': [{'j': 9},
                  {'g': 7, 'h': 8}],
            'c': {'d': 4,
                  'e': {'f': 6}}}


def test_encode_resources():
    pb = Cpus(0.1)
    assert pb.scalar.value == 0.1
    assert pb.name == 'cpus'
    assert pb.type == "SCALAR"

    pb = Mem(16)
    assert pb.scalar.value == 16
    assert pb.name == 'mem'
    assert pb.type == "SCALAR"

    pb = Disk(256)
    assert pb.scalar.value == 256
    assert pb.name == 'disk'
    assert pb.type == "SCALAR"


def test_task_info_resources():
    task = TaskInfo.encode(dict(name='test-task',
                    task_id=dict(value='test-task-id'),
                    resources=[Cpus(0.1), Mem(16)],))
    pb = task
    assert pb.name == 'test-task'
    assert pb.task_id.value == 'test-task-id'
    assert pb.resources[0].name == 'cpus'
    assert pb.resources[0].scalar.value == 0.1
    assert pb.resources[1].name == 'mem'
    assert pb.resources[1].scalar.value == 16




def test_scalar_resource_comparison():
    r1 = ScalarResource(value=11.5)

    assert r1 == ScalarResource(value=11.5)

    assert r1 >= ScalarResource(value=11.5)
    assert r1 <= ScalarResource(value=11.5)
    assert r1 < ScalarResource(value=12)
    assert r1 > ScalarResource(value=11)

    assert r1 == 11.5
    assert r1 <= 11.5
    assert r1 >= 11.5
    assert r1 < 12
    assert r1 > 11


def test_scalar_resource_addition():
    r1 = ScalarResource(value=11.5)
    r2 = ScalarResource(value=2)

    s = r1 + r2
    assert isinstance(s, ScalarResource)
    assert s == ScalarResource(13.5)
    assert s == 13.5


def test_scalar_resource_sum():
    r1 = ScalarResource(value=11.5)
    r2 = ScalarResource(value=2)
    r3 = ScalarResource(value=3)

    s = sum([r1, r2, r3])
    assert isinstance(s, ScalarResource)
    assert s == ScalarResource(16.5)
    assert s == 16.5


def test_scalar_resource_subtraction():
    r1 = ScalarResource(value=11.5)
    r2 = ScalarResource(value=2)

    s = r1 - r2
    assert isinstance(s, ScalarResource)
    assert s == ScalarResource(9.5)
    assert s == 9.5


def test_scalar_resource_inplace_addition():
    r1 = ScalarResource(value=11.5)
    r2 = ScalarResource(value=2)

    r1 += r2
    assert isinstance(r1, ScalarResource)
    assert r1 == ScalarResource(13.5)
    assert r1 == 13.5


def test_scalar_resource_inplace_subtraction():
    r1 = ScalarResource(value=11.5)
    r2 = ScalarResource(value=2)

    r1 -= r2
    assert isinstance(r1, ScalarResource)
    assert r1 == ScalarResource(9.5)
    assert r1 == 9.5


def test_scalar_resource_multiplication():
    r1 = ScalarResource(value=11.5)
    r2 = ScalarResource(value=2)

    m = r1 * r2
    assert isinstance(m, ScalarResource)
    assert m == ScalarResource(23)
    assert m == 23


def test_scalar_resource_division():
    r1 = ScalarResource(value=11.5)
    r2 = ScalarResource(value=2)

    d = r1 / r2
    assert isinstance(d, ScalarResource)
    assert d == ScalarResource(5.75)
    assert d == 5.75


def test_resources_mixin_comparison():
    o1 = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    o2 = Offer(resources=[Cpus(2), Mem(256), Disk(1024)])

    t1 = TaskInfo.encode(dict(resources=[Cpus(0.5), Mem(128), Disk(0)]))
    t2 = TaskInfo.encode(dict(resources=[Cpus(1), Mem(256), Disk(512)]))
    t3 = TaskInfo.encode(dict(resources=[Cpus(0.5), Mem(256), Disk(512)]))

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


def test_resources_mixin_addition():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    t = TaskInfo.encode(dict(resources=[Cpus(0.5), Mem(128), Disk(0)]))

    s = o + t
    assert isinstance(s, ResourcesMixin)
    assert s.cpus == Cpus(1.5)
    assert s.cpus == 1.5
    assert s.mem == Mem(256)
    assert s.mem == 256
    assert s.disk == Disk(0)
    assert s.disk == 0


def test_resources_mixin_sum():
    o1 = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    o2 = Offer(resources=[Cpus(2), Mem(128), Disk(100)])
    o3 = Offer(resources=[Cpus(0.5), Mem(256), Disk(200)])

    s = sum([o1, o2, o3])
    assert isinstance(s, ResourcesMixin)
    assert s.cpus == Cpus(3.5)
    assert s.cpus == 3.5
    assert s.mem == Mem(512)
    assert s.mem == 512
    assert s.disk == Disk(300)
    assert s.disk == 300


def test_resources_mixin_subtraction():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(0)])
    t = TaskInfo.encode(dict(resources=[Cpus(0.5), Mem(128), Disk(0)]))

    s = o - t
    assert isinstance(s, ResourcesMixin)
    assert s.cpus == Cpus(0.5)
    assert s.cpus == 0.5
    assert s.mem == Mem(0)
    assert s.mem == 0
    assert s.disk == Disk(0)
    assert s.disk == 0


def test_resources_mixin_inplace_addition():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(64)])
    t = TaskInfo.encode(dict(resources=[Cpus(0.5), Mem(128), Disk(0)]))

    o += t
    assert isinstance(o, Offer)
    assert o.cpus == Cpus(1.5)
    assert o.cpus == 1.5
    assert o.mem == Mem(256)
    assert o.mem == 256
    assert o.disk == Disk(64)
    assert o.disk == 64


def test_resources_mixin_inplace_subtraction():
    o = Offer(resources=[Cpus(1), Mem(128), Disk(64)])
    t = TaskInfo.encode(dict(resources=[Cpus(0.5), Mem(128), Disk(0)]))

    o -= t
    assert isinstance(o, Offer)
    assert o.cpus == Cpus(0.5)
    assert o.cpus == 0.5
    assert o.mem == Mem(0)
    assert o.mem == 0
    assert o.disk == Disk(64)
    assert o.disk == 64


def test_status_in_task_info():
    t = TaskInfo.encode(dict(name='test-task',
                 task_id=dict(value='test-task-id'),
                 resources=[Cpus(0.1), Mem(16)],
                 command=dict(value='echo 100')))

    assert isinstance(t.status, TaskStatus)
    assert t.status.state == 'TASK_STAGING'

    p = t
    assert isinstance(p, TaskInfo)
    #TODO Whats the point of this?
    # with pytest.raises(AttributeError):
    #     p.status


def test_encode_task_info():
    t = TaskInfo.encode(dict(name='test-task',
                 task_id=dict(value='test-task-id'),
                 resources=[Cpus(0.1), Mem(16)],
                 command=dict(value='echo 100')))

    p = t
    assert isinstance(p, TaskInfo)
    assert p.command.value == 'echo 100'
    assert p.name == 'test-task'
    assert p.resources[0].name == 'cpus'
    assert p.resources[0].scalar.value == 0.1
    assert p.task_id.value == 'test-task-id'


def test_non_strict_encode_task_info():
    t = TaskInfo.encode(dict(name='test-task',
                 task_id=dict(value='test-task-id'),
                 resources=[Cpus(0.1), Mem(16)],
                 command=dict(value='echo 100')))
    t.result = 'some binary data'
    t.status = TaskStatus()

    p = t
    assert isinstance(p, TaskInfo)
    assert p.command.value == 'echo 100'
    # TODO Whats the point of this?
    # with pytest.raises(AttributeError):
    #     p.status

def test_json():
    o1 = Offer(resources=[Cpus(1), Mem(128), Disk(0)])

    t1 = TaskInfo.encode(dict(resources=[Cpus(0.5), Mem(128), Disk(0)]))

    assert o1 == Offer.encode(json.loads(json.dumps(o1)))
    assert t1 == TaskInfo.encode(json.loads(json.dumps(t1)))