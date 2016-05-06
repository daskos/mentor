from __future__ import absolute_import, division, print_function

import pytest
from mesos.interface import mesos_pb2
from satyr.proxies.messages import (CommandInfo, Cpus, Disk, FrameworkID,
                                    FrameworkInfo, Map, Mem, MessageProxy,
                                    Offer, RegisterProxies, ResourcesMixin,
                                    ScalarResource, TaskID, TaskInfo,
                                    TaskStatus, decode, encode)


@pytest.fixture
def d():
    return {'a': 1,
            'b': [{'j': 9},
                  {'g': 7, 'h': 8}],
            'c': {'d': 4,
                  'e': {'f': 6}}}


def test_map_init(d):
    m = Map(**d)
    assert isinstance(m, Map)
    assert isinstance(m, dict)


def test_map_get(d):
    m = Map(**d)
    assert m['a'] == 1
    assert m['c']['e']['f'] == 6
    assert m['b'][0]['j'] == 9
    assert m['b'][1]['g'] == 7
    assert isinstance(m['b'], list)
    assert isinstance(m['b'][1], Map)


def test_map_dot_get(d):
    m = Map(**d)
    assert m.a == 1
    assert m.c.e.f == 6
    assert m.b[0].j == 9
    assert m.b[1].g == 7
    assert isinstance(m.b, list)
    assert isinstance(m.b[1], Map)


def test_map_set(d):
    m = Map(**d)
    m['A'] = 11
    m['a'] = 'one'
    m['z'] = {'Z': {'omega': 20}}
    assert m['a'] == 'one'
    assert m['A'] == 11
    assert m['z']['Z']['omega'] == 20
    assert isinstance(m['z'], Map)
    assert isinstance(m['z']['Z'], Map)


def test_map_dot_set(d):
    m = Map(**d)
    m.A = 11
    m.a = 'one'
    m.z = {'Z': {'omega': 20}}
    assert m.a == 'one'
    assert m.A == 11
    assert m.z.Z.omega == 20
    assert isinstance(m.z, Map)
    assert isinstance(m.z.Z, Map)


# def test_map_set_missing(d):
#     m = Map(**d)
#     m['y']['o']['w'] = 9
#     m.y.w.o = 6

#     assert m['y']['o']['w'] == 9
#     assert m.y.w.o == 6


def test_hash():
    d1 = Map(a=Map(b=3), c=5)
    d2 = Map(a=Map(b=3), c=5)
    d3 = Map(a=Map(b=6), c=5)

    assert hash(d1) == hash(d2)
    assert hash(d1) != hash(d3)
    assert hash(d2) != hash(d3)


def test_dict_hashing():
    d2 = Map(a=Map(b=3), c=5)
    d3 = Map(a=Map(b=6), c=5)

    c = {}
    c[d2.a] = d2
    c[d3.a] = d3

    assert c[d2.a] == d2
    assert c[d3.a] == d3


def test_register_proxies():
    class Base(object):
        __metaclass__ = RegisterProxies
        proto = 'base'

    class First(Base):
        proto = 'first'

    class Second(Base):
        proto = 'second'

    class Third(Base):
        proto = 'third'

    assert Base.registry == [('third', Third),
                             ('second', Second),
                             ('first', First),
                             ('base', Base)]


def test_encode_resources():
    pb = encode(Cpus(0.1))
    assert pb.scalar.value == 0.1
    assert pb.name == 'cpus'
    assert pb.type == mesos_pb2.Value.SCALAR

    pb = encode(Mem(16))
    assert pb.scalar.value == 16
    assert pb.name == 'mem'
    assert pb.type == mesos_pb2.Value.SCALAR

    pb = encode(Disk(256))
    assert pb.scalar.value == 256
    assert pb.name == 'disk'
    assert pb.type == mesos_pb2.Value.SCALAR


def test_encode_task_info_resources():
    task = TaskInfo(name='test-task',
                    id=TaskID(value='test-task-id'),
                    resources=[Cpus(0.1), Mem(16)],
                    command=CommandInfo(value='testcmd'))
    pb = encode(task)
    assert pb.name == 'test-task'
    assert pb.task_id.value == 'test-task-id'
    assert pb.resources[0].name == 'cpus'
    assert pb.resources[0].scalar.value == 0.1
    assert pb.resources[1].name == 'mem'
    assert pb.resources[1].scalar.value == 16
    assert pb.command.value == 'testcmd'


def test_decode_framework_info():
    message = mesos_pb2.FrameworkInfo(id=mesos_pb2.FrameworkID(value='test'))
    wrapped = decode(message)

    assert isinstance(wrapped, MessageProxy)
    assert isinstance(wrapped, FrameworkInfo)
    assert isinstance(wrapped.id, MessageProxy)
    assert isinstance(wrapped.id, FrameworkID)


def test_scalar_resource_comparison():
    r1 = ScalarResource(value=11.5)

    assert r1 == ScalarResource(value=11.5)
    assert r1 <= ScalarResource(value=11.5)
    assert r1 >= ScalarResource(value=11.5)
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

    t1 = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])
    t2 = TaskInfo(resources=[Cpus(1), Mem(256), Disk(512)])
    t3 = TaskInfo(resources=[Cpus(0.5), Mem(256), Disk(512)])

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
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

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
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

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
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

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
    t = TaskInfo(resources=[Cpus(0.5), Mem(128), Disk(0)])

    o -= t
    assert isinstance(o, Offer)
    assert o.cpus == Cpus(0.5)
    assert o.cpus == 0.5
    assert o.mem == Mem(0)
    assert o.mem == 0
    assert o.disk == Disk(64)
    assert o.disk == 64


def test_encode_task_info():
    t = TaskInfo(name='test-task',
                 id=TaskID(value='test-task-id'),
                 resources=[Cpus(0.1), Mem(16)],
                 command=CommandInfo(value='echo 100'))

    p = encode(t)
    assert isinstance(p, mesos_pb2.TaskInfo)
    assert p.command.value == 'echo 100'
    assert p.name == 'test-task'
    assert p.resources[0].name == 'cpus'
    assert p.resources[0].scalar.value == 0.1
    assert p.task_id.value == 'test-task-id'


def test_non_strict_encode_task_info():
    t = TaskInfo(name='test-task',
                 id=TaskID(value='test-task-id'),
                 resources=[Cpus(0.1), Mem(16)],
                 command=CommandInfo(value='echo 100'))
    t.result = 'some binary data'
    t.status = TaskStatus()

    p = encode(t)
    assert isinstance(p, mesos_pb2.TaskInfo)
    assert p.command.value == 'echo 100'
    with pytest.raises(AttributeError):
        p.status
