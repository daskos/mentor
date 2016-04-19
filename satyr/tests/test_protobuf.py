from __future__ import absolute_import, division, print_function

import pytest
from sample_pb2 import MessageOfTypes
from satyr.protobuf import dict_to_protobuf, protobuf_to_dict


@pytest.fixture
def m():
    m = MessageOfTypes()
    m.dubl = 1.7e+308
    m.flot = 3.4e+038
    m.i32 = 2 ** 31 - 1  # 2147483647 #
    m.i64 = 2 ** 63 - 1  # 0x7FFFFFFFFFFFFFFF
    m.ui32 = 2 ** 32 - 1
    m.ui64 = 2 ** 64 - 1
    m.si32 = -1 * m.i32
    m.si64 = -1 * m.i64
    m.f32 = m.i32
    m.f64 = m.i64
    m.sf32 = m.si32
    m.sf64 = m.si64
    m.bol = True
    m.strng = "string"
    m.byts = b'\n\x14\x1e'
    assert len(m.byts) == 3, len(m.byts)
    m.nested.req = "req"
    m.enm = MessageOfTypes.C  # @UndefinedVariable
    m.enmRepeated.extend([MessageOfTypes.A, MessageOfTypes.C])
    m.range.extend(range(10))
    return m


def compare(m, d, exclude=None):
    i = 0
    exclude = ['byts', 'nested', 'enm', 'enmRepeated'] + (exclude or [])
    for i, field in enumerate(MessageOfTypes.DESCRIPTOR.fields):  # @UndefinedVariable
        if field.name not in exclude:
            assert field.name in d, field.name
            assert d[field.name] == getattr(
                m, field.name), (field.name, d[field.name])
    assert i > 0
    assert m.byts == str(d['byts'])
    assert d['nested'] == {'req': m.nested.req}


def test_basics(m):
    d = protobuf_to_dict(m)
    compare(m, d, ['nestedRepeated'])

    m2 = dict_to_protobuf(d, MessageOfTypes)
    assert m == m2


def test_use_enum_labels(m):
    d = protobuf_to_dict(m)
    compare(m, d, ['nestedRepeated'])
    assert d['enm'] == 'C'
    assert d['enmRepeated'] == ['A', 'C']

    m2 = dict_to_protobuf(d, MessageOfTypes)
    assert m == m2

    d['enm'] = 'MEOW'
    with pytest.raises(KeyError):
        dict_to_protobuf(d, MessageOfTypes)

    d['enm'] = 'A'
    d['enmRepeated'] = ['B']
    dict_to_protobuf(d, MessageOfTypes)

    d['enmRepeated'] = ['CAT']
    with pytest.raises(KeyError):
        dict_to_protobuf(d, MessageOfTypes)


def test_repeated_enum(m):
    d = protobuf_to_dict(m)
    compare(m, d, ['nestedRepeated'])
    assert d['enmRepeated'] == ['A', 'C']

    m2 = dict_to_protobuf(d, MessageOfTypes)
    assert m == m2

    d['enmRepeated'] = ['MEOW']
    with pytest.raises(KeyError):
        dict_to_protobuf(d, MessageOfTypes)


def test_nested_repeated(m):
    m.nestedRepeated.extend(
        [MessageOfTypes.NestedType(req=str(i)) for i in range(10)])

    d = protobuf_to_dict(m)
    compare(m, d, exclude=['nestedRepeated'])
    assert d['nestedRepeated'] == [{'req': str(i)} for i in range(10)]

    m2 = dict_to_protobuf(d, MessageOfTypes)
    assert m == m2


def test_reverse(m):
    m2 = dict_to_protobuf(protobuf_to_dict(m), MessageOfTypes)
    assert m == m2
    m2.dubl = 0
    assert m2 != m


def test_incomplete(m):
    d = protobuf_to_dict(m)
    d.pop('dubl')
    m2 = dict_to_protobuf(d, MessageOfTypes)
    assert m2.dubl == 0
    assert m != m2


def test_non_strict(m):
    d = protobuf_to_dict(m)
    d['non_existing_field'] = 'data'
    d['temporary_field'] = 'helping_state'

    with pytest.raises(KeyError):
        dict_to_protobuf(d, MessageOfTypes)

    m2 = dict_to_protobuf(d, MessageOfTypes, strict=False)
    with pytest.raises(AttributeError):
        m2.temporary_field


def test_pass_instance(m):
    d = protobuf_to_dict(m)
    d['dubl'] = 1
    m2 = dict_to_protobuf(d, m)
    assert m is m2
    assert m.dubl == 1


def test_container_mapping(m):
    class mapping(dict):
        pass

    containers = [(MessageOfTypes.NestedType(), mapping),
                  (MessageOfTypes(), dict)]

    m.nestedRepeated.extend([MessageOfTypes.NestedType(req='1')])
    d = protobuf_to_dict(m, containers=containers)
    m = dict_to_protobuf(d, containers=containers)

    assert isinstance(d, dict)
    assert isinstance(d['nested'], mapping)
    assert isinstance(m, MessageOfTypes)
    assert isinstance(m.nested, MessageOfTypes.NestedType)


def test_conditional_container_mapping(m):
    class truedict(dict):
        pass

    class falsedict(dict):
        pass

    containers = [(MessageOfTypes(bol=True), truedict),
                  (MessageOfTypes(bol=False), falsedict),
                  (MessageOfTypes.NestedType(), dict)]

    m.bol = True
    d = protobuf_to_dict(m, containers=containers)
    p = dict_to_protobuf(d, containers=containers)

    assert isinstance(d, truedict)
    assert isinstance(p, MessageOfTypes)

    m.bol = False
    d = protobuf_to_dict(m, containers=containers)
    p = dict_to_protobuf(d, containers=containers)

    assert isinstance(d, falsedict)
    assert isinstance(p, MessageOfTypes)
