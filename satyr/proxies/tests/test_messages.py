import pytest
from mesos.interface import mesos_pb2
from satyr.proxies.messages import (FrameworkID, FrameworkInfo, Map,
                                    MessageProxy, RegisterProxies, decode)


@pytest.fixture
def d():
    return {'a': 1,
            'b': [{'j': 9},
                  {'g': 7, 'h': 8}],
            'c': {'d': 4,
                  'e': {'f': 6}}}


def test_map_init(d):
    m = Map(d)
    assert isinstance(m, Map)
    assert isinstance(m, dict)


def test_map_get(d):
    m = Map(d)
    assert m['a'] == 1
    assert m['c']['e']['f'] == 6
    assert m['b'][0]['j'] == 9
    assert m['b'][1]['g'] == 7
    assert isinstance(m['b'], list)
    assert isinstance(m['b'][1], Map)


def test_map_dot_get(d):
    m = Map(d)
    assert m.a == 1
    assert m.c.e.f == 6
    assert m.b[0].j == 9
    assert m.b[1].g == 7
    assert isinstance(m.b, list)
    assert isinstance(m.b[1], Map)


def test_map_set(d):
    m = Map(d)
    m['A'] = 11
    m['a'] = 'one'
    m['z'] = {'Z': {'omega': 20}}
    assert m['a'] == 'one'
    assert m['A'] == 11
    assert m['z']['Z']['omega'] == 20
    assert isinstance(m['z'], Map)
    assert isinstance(m['z']['Z'], Map)


def test_map_dot_set(d):
    m = Map(d)
    m.A = 11
    m.a = 'one'
    m.z = {'Z': {'omega': 20}}
    assert m.a == 'one'
    assert m.A == 11
    assert m.z.Z.omega == 20
    assert isinstance(m.z, Map)
    assert isinstance(m.z.Z, Map)


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


def test_framework_info():
    message = mesos_pb2.FrameworkInfo(id=mesos_pb2.FrameworkID(value='test'))
    wrapped = decode(message)

    assert isinstance(wrapped, MessageProxy)
    assert isinstance(wrapped, FrameworkInfo)
    assert isinstance(wrapped.id, MessageProxy)
    assert isinstance(wrapped.id, FrameworkID)
