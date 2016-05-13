from __future__ import absolute_import, division, print_function

import operator
from functools import partial
from uuid import uuid4

from google.protobuf.message import Message
from mesos.interface import mesos_pb2

from .. import protobuf


class Map(dict):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            # self[k] = v

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

    # def __missing__(self, k):
    #    # TODO: consider not using this, silents errors
    #    self[k] = Map()
    #    return self[k]

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


class Environment(MessageProxy):
    proto = mesos_pb2.Environment


class Scalar(MessageProxy):
    proto = mesos_pb2.Value.Scalar


class Resource(MessageProxy):
    proto = mesos_pb2.Resource


# TODO: RangeResource e.g. ports
class ScalarResource(Resource):
    # supports comparison and basic arithmetics with scalars
    proto = mesos_pb2.Resource(type=mesos_pb2.Value.SCALAR)

    def __init__(self, value=None, **kwargs):
        super(Resource, self).__init__(**kwargs)
        if value is not None:
            self.scalar = Scalar(value=value)

    def __cmp__(self, other):
        first, second = float(self), float(other)
        if first < second:
            return -1
        elif first > second:
            return 1
        else:
            return 0

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.scalar.value)

    def __float__(self):
        return float(self.scalar.value)

    @classmethod
    def _op(cls, op, first, second):
        value = op(float(first), float(second))
        return cls(value=value)

    def __add__(self, other):
        return self._op(operator.add, self, other)

    def __radd__(self, other):
        return self._op(operator.add, other, self)

    def __sub__(self, other):
        return self._op(operator.sub, self, other)

    def __rsub__(self, other):
        return self._op(operator.sub, other, self)

    def __mul__(self, other):
        return self._op(operator.mul, self, other)

    def __rmul__(self, other):
        return self._op(operator.mul, other, self)

    def __truediv__(self, other):
        return self._op(operator.truediv, self, other)

    def __rtruediv__(self, other):
        return self._op(operator.truediv, other, self)

    def __iadd__(self, other):
        self.scalar.value = float(self._op(operator.add, self, other))
        return self

    def __isub__(self, other):
        self.scalar.value = float(self._op(operator.sub, self, other))
        return self


class Cpus(ScalarResource):
    proto = mesos_pb2.Resource(name='cpus', type=mesos_pb2.Value.SCALAR)


class Mem(ScalarResource):
    proto = mesos_pb2.Resource(name='mem', type=mesos_pb2.Value.SCALAR)


class Disk(ScalarResource):
    proto = mesos_pb2.Resource(name='disk', type=mesos_pb2.Value.SCALAR)


class ResourcesMixin(object):

    @classmethod
    def _cast_zero(cls, other=0):
        if other == 0:
            return cls(resources=[Cpus(0), Mem(0), Disk(0)])
        else:
            return other

    @property
    def cpus(self):
        for res in self.resources:
            if isinstance(res, Cpus):
                return res
        return Cpus(0.0)

    @property
    def mem(self):
        for res in self.resources:
            if isinstance(res, Mem):
                return res
        return Mem(0.0)

    @property
    def disk(self):
        for res in self.resources:
            if isinstance(res, Disk):
                return res
        return Disk(0.0)

    # @property
    # def ports(self):
    #     for res in self.resources:
    #         if isinstance(res, Ports):
    #             return [(rng.begin, rng.end) for rng in res.ranges.range]

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__,
                                 ', '.join(map(str, self.resources)))

    def __cmp__(self, other):
        other = self._cast_zero(other)

        if all([self.cpus < other.cpus,
                self.mem < other.mem,
                self.disk < other.disk]):
            # all resources are smaller the task will fit into offer
            return -1
        elif any([self.cpus > other.cpus,
                  self.mem > other.mem,
                  self.disk > other.disk]):
            # any resources is bigger task won't fit into offer
            return 1
        else:
            return 0

    def __radd__(self, other):  # to support sum()
        other = self._cast_zero(other)
        return self + other

    def __add__(self, other):
        other = self._cast_zero(other)
        # ports = list(set(self.ports) | set(other.ports))
        cpus = self.cpus + other.cpus
        mem = self.mem + other.mem
        disk = self.disk + other.disk
        mixin = self.__class__()
        mixin.resources = [cpus, disk, mem]
        return mixin

    def __sub__(self, other):
        other = self._cast_zero(other)
        # ports = list(set(self.ports) | set(other.ports))
        cpus = self.cpus - other.cpus
        mem = self.mem - other.mem
        disk = self.disk - other.disk
        mixin = self.__class__()
        mixin.resources = [cpus, disk, mem]
        return mixin

    def __iadd__(self, other):
        other = self._cast_zero(other)
        added = self + other
        self.resources = added.resources
        return self

    def __isub__(self, other):
        other = self._cast_zero(other)
        subbed = self - other
        self.resources = subbed.resources
        return self


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

    def __init__(self, id=None, **kwargs):
        super(ExecutorInfo, self).__init__(**kwargs)
        self.id = id or str(uuid4())

    @property
    def id(self):  # more consistent naming
        return self['executor_id']

    @id.setter
    def id(self, value):
        if not isinstance(value, ExecutorID):
            value = ExecutorID(value=value)
        self['executor_id'] = value


class MasterInfo(MessageProxy):
    proto = mesos_pb2.MasterInfo


class SlaveInfo(MessageProxy):
    proto = mesos_pb2.SlaveInfo


class Filters(MessageProxy):
    proto = mesos_pb2.Filters


class TaskStatus(MessageProxy):
    proto = mesos_pb2.TaskStatus

    @property
    def task_id(self):  # more consistent naming
        return self['task_id']

    @task_id.setter
    def task_id(self, value):
        if not isinstance(value, TaskID):
            value = TaskID(value=value)
        self['task_id'] = value

    def is_staging(self):
        return self.state == 'TASK_STAGING'

    def is_starting(self):
        return self.state == 'TASK_STARTING'

    def is_running(self):
        return self.state == 'TASK_RUNNING'

    def has_succeeded(self):
        return self.state == 'TASK_FINISHED'

    def has_failed(self):
        return self.state in ['TASK_FAILED', 'TASK_LOST', 'TASK_KILLED',
                              'TASK_ERROR']

    def has_terminated(self):
        return self.has_succeeded() or self.has_failed()


class Offer(ResourcesMixin, MessageProxy):  # important order!
    proto = mesos_pb2.Offer


class TaskInfo(ResourcesMixin, MessageProxy):
    proto = mesos_pb2.TaskInfo

    def __init__(self, id=None, **kwargs):
        super(TaskInfo, self).__init__(**kwargs)
        self.id = id or str(uuid4())

    @property
    def id(self):  # more consistent naming
        return self['task_id']

    @id.setter
    def id(self, value):
        if not isinstance(value, TaskID):
            value = TaskID(value=value)
        self['task_id'] = value

    def status(self, state, **kwargs):  # used on executor side
        return TaskStatus(task_id=self.id, state=state, **kwargs)


class CommandInfo(MessageProxy):
    proto = mesos_pb2.CommandInfo


class ContainerInfo(MessageProxy):
    proto = mesos_pb2.ContainerInfo


class DockerInfo(MessageProxy):
    proto = mesos_pb2.ContainerInfo.DockerInfo


class Request(MessageProxy):
    proto = mesos_pb2.Request


class Operation(MessageProxy):
    proto = mesos_pb2.Offer.Operation


decode = partial(protobuf.decode, containers=MessageProxy.registry)
encode = partial(protobuf.encode, containers=MessageProxy.registry,
                 strict=False)
