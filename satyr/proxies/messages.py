from __future__ import absolute_import, division, print_function

import logging
from functools import partial
from uuid import uuid4

from google.protobuf.message import Message
from mesos.interface import mesos_pb2

from .. import protobuf


class Map(dict):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self[k] = v

    @classmethod
    def cast(cls, v):
        if isinstance(v, Map):
            return v
        elif isinstance(v, dict):
            return Map(**v)
        elif hasattr(v, '__iter__'):
            return map(cls.cast, v)
        else:
            return v

    def __setitem__(self, k, v):
        # accidental __missing__ call will create a new node
        super(Map, self).__setitem__(k, self.cast(v))

    def __setattr__(self, k, v):
        prop = getattr(self.__class__, k, None)
        if isinstance(prop, property):  # property binding
            prop.fset(self, v)
        elif callable(v):  # method binding
            self.__dict__[k] = v
        else:
            self[k] = v

    def __getattr__(self, k):
        return self[k]

    # def __delattr__(self, k):
    #    del self[k]

    def __missing__(self, k):  # TODO: consider not using this, silents errors
        self[k] = Map()
        return self[k]

    def __hash__(self):
        return hash(tuple(self.items()))


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


class MessageProxy(Map):
    __metaclass__ = RegisterProxies
    proto = Message


class ResourcesMixin(object):

    def get_scalar(self, cls):
        for res in self.resources:
            if isinstance(res, cls):
                return res.scalar.value

    @property
    def cpus(self):
        return self.get_scalar(Cpus)

    @property
    def mem(self):
        return self.get_scalar(Mem)

    @property
    def disk(self):
        return self.get_scalar(Disk)

    # @property
    # def ports(self):
    #     for res in self.resources:
    #         if isinstance(res, Ports):
    #             return [(rng.begin, rng.end) for rng in res.ranges.range]

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
    #    mem = self.mem + other.mem

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

    def has_succeeded(self):
        return self.state == 'TASK_FINISHED'

    def has_failed(self):
        return self.state in ['TASK_FAILED', 'TASK_LOST', 'TASK_KILLED']

    def has_terminated(self):
        return self.has_succeeded() or self.has_failed()


class Offer(ResourcesMixin, MessageProxy):  # important order!
    proto = mesos_pb2.Offer


class TaskInfo(ResourcesMixin, MessageProxy):
    proto = mesos_pb2.TaskInfo

    def __init__(self, id=None, **kwargs):
        super(TaskInfo, self).__init__(**kwargs)
        self.id = id or TaskID(value=str(uuid4()))

    @property
    def id(self):  # more consistent naming
        return self.task_id

    @id.setter
    def id(self, value):
        self.task_id = value

    def status(self, state, **kwargs):  # used on executor side
        return TaskStatus(task_id=self.task_id, state=state, **kwargs)

    def update(self, status):
        self.on_update(status)

        if status.has_succeeded():
            self.on_success(status)
        elif status.has_failed():
            self.on_fail(status)

    def on_update(self, status):
        pass

    def on_success(self, status):
        pass

    def on_fail(self, status):
        pass


class CommandInfo(MessageProxy):
    proto = mesos_pb2.CommandInfo


class ContainerInfo(MessageProxy):
    proto = mesos_pb2.ContainerInfo


class Request(MessageProxy):
    proto = mesos_pb2.Request


class Operation(MessageProxy):
    proto = mesos_pb2.Offer.Operation


decode = partial(protobuf.decode, containers=MessageProxy.registry)
encode = partial(protobuf.encode, containers=MessageProxy.registry,
                 strict=False)
