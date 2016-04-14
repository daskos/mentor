import pytest
from mesos.interface import mesos_pb2
from satyr.proxies.messages import (CommandInfo, Cpus, Disk, FrameworkID,
                                    FrameworkInfo, Map, Mem, MessageProxy,
                                    RegisterProxies, TaskID, TaskInfo, decode,
                                    encode)


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


def test_map_set_missing(d):
    m = Map(**d)
    m['y']['o']['w'] = 9
    m.y.w.o = 6

    assert m['y']['o']['w'] == 9
    assert m.y.w.o == 6


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


def test_encode_task_info():
    task = TaskInfo(name='test-task',
                    task_id=TaskID(value='test-task-id'),
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
