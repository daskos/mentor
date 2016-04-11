from __future__ import absolute_import, division, print_function

from functools import partial

from google.protobuf.message import Message
from mesos.interface import mesos_pb2

from .. import protobuf


class Map(dict):

    def __init__(self, mapping=None, **kwargs):
        mapping = mapping or kwargs
        for k, v in mapping.items():
            if isinstance(v, dict):
                mapping[k] = Map(mapping=v)
            elif hasattr(v, '__iter__'):
                mapping[k] = [Map(mapping=i) for i in v]
        super(Map, self).__init__(mapping)
        #self.__dict__ = self

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError('No such attribute: {}'.format(name))

    def __missing__(self, name):
        self[name] = Map()
        return self[name]

    def __hash__(self):
        return hash(frozenset(self))


class RegisterProxies(type):

    def __init__(cls, name, bases, nmspc):
        super(RegisterProxies, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = []
        cls.registry.insert(0, (cls.proto, cls))
        # cls.registry -= set(bases) # Remove base classes

    # Metamethods, called on class objects:
    def __iter__(cls):
        return iter(cls.registry)

    def __str__(cls):
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])


class MessageProxy(Map):
    __metaclass__ = RegisterProxies
    proto = Message


class ResourcesMixin(object):

    @property
    def cpus(self):
        for res in self.resources:
            if res.name == 'cpus':
                return res.scalar.value

    @property
    def mem(self):
        for res in self.resources:
            if res.name == 'mem':
                return res.scalar.value

    @property
    def disk(self):
        for res in self.resources:
            if res.name == 'disk':
                return res.scalar.value

    @property
    def ports(self):
        for res in self.resources:
            if res.name == 'ports':
                return [(rng.begin, rng.end) for rng in res.ranges.range]

    def __cmp__(self, other):
        this = (self.cpus, self.mem, self.disk)
        other = (other.cpus, other.mem, other.disk)
        if this < other:
            return -1
        elif this > other:
            return 1
        else:
            return 0

    # def __add__(self, other):
    #     ports = list(set(self.ports) | set(other.ports))
    #     disk = self.disk + other.disk
    #     cpus = self.cpus + other.cpus
    #     mem = self.mem + other.mem
    #     return Resources(cpus=cpus, mem=mem, disk=disk, ports=ports)

    # def __sub__(self, other):
    #     ports = list(set(self.ports) - set(other.ports))
    #     disk = self.disk - other.disk
    #     cpus = self.cpus - other.cpus
    #     mem = self.mem - other.mem
    #     return Resources(cpus=cpus, mem=mem, disk=disk, ports=ports)


class Resource(MessageProxy):
    proto = mesos_pb2.Resource

    def __init__(self, value=None, **kwargs):
        super(Resource, self).__init__(**kwargs)
        if value is not None:
            self.scalar.value = value


class Cpus(Resource):
    proto = mesos_pb2.Resource(name='cpus', type=mesos_pb2.Value.SCALAR)


class Mem(Resource):
    proto = mesos_pb2.Resource(name='mem', type=mesos_pb2.Value.SCALAR)


class Disk(Resource):
    proto = mesos_pb2.Resource(name='disk', type=mesos_pb2.Value.SCALAR)


class FrameworkID(MessageProxy):
    proto = mesos_pb2.FrameworkID


class SlaveID(MessageProxy):
    proto = mesos_pb2.SlaveID


class ExecutorID(MessageProxy):
    proto = mesos_pb2.ExecutorID


class OfferID(MessageProxy):
    proto = mesos_pb2.OfferID


class TaskID(MessageProxy):
    proto = mesos_pb2.TaskID


class FrameworkInfo(MessageProxy):
    proto = mesos_pb2.FrameworkInfo


class ExecutorInfo(MessageProxy):
    proto = mesos_pb2.ExecutorInfo


class MasterInfo(MessageProxy):
    proto = mesos_pb2.MasterInfo


class SlaveInfo(MessageProxy):
    proto = mesos_pb2.SlaveInfo


class Filters(MessageProxy):
    proto = mesos_pb2.Filters


class TaskStatus(MessageProxy):
    proto = mesos_pb2.TaskStatus


class Offer(MessageProxy, ResourcesMixin):
    proto = mesos_pb2.Offer


class TaskInfo(MessageProxy, ResourcesMixin):
    proto = mesos_pb2.TaskInfo

    def status(self, state, message='', data=None):
        return TaskStatus(task_id=self.id, state=state, message=message,
                          data=data)


class CommandInfo(MessageProxy):
    proto = mesos_pb2.CommandInfo


class ContainerInfo(MessageProxy):
    proto = mesos_pb2.ContainerInfo

encode = partial(protobuf.encode, containers=MessageProxy.registry)
decode = partial(protobuf.decode, containers=MessageProxy.registry)
