from __future__ import absolute_import, division, print_function

import operator
from functools import partial
from uuid import uuid4
import six


class Message(dict):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            # self[k] = v

    @classmethod
    def cast(cls, v):
        if isinstance(v, Message):
            return v
        elif isinstance(v, dict):
            return Message(**v)
        elif isinstance(v, (str, bytes)):
            return v
        elif hasattr(v, '__iter__'):
            return [cls.cast(item) for item in v]
        else:
            return v

    def __setitem__(self, k, v):
        # accidental __missing__ call will create a new node
        super(Message, self).__setitem__(k, self.cast(v))

    def __setattr__(self, k, v):
        prop = getattr(self.__class__, k, None)
        if isinstance(prop, property):  # property binding
            prop.fset(self, v)
        # elif hasattr(v, '__call__'):  # method binding, not sure why?
        #     self.__dict__[k] = v
        else:
            self[k] = v

    def __getattr__(self, k):
        if k != "__call__":
            return self[k]

    def __dir__(self):
        return super().__dir__() + [str(k) for k in self.keys()]

    # def __delattr__(self, k):
    #    del self[k]

    # def __missing__(self, k):
    #    # TODO: consider not using this, silents errors
    #    self[k] = Map()
    #    return self[k]

    def __hash__(self):
        return hash(tuple(self.items()))


class Variable(Message):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Environment(Message):
    def __init__(self, **kwargs):

        # self.variables = []
        # if not isinstance(variables, dict):
        #     raise TypeError("Expecting a dict of variables")
        # for name, value in six.iteritems(variables):
        #     self.variables.append(Variable(name, value))
        super(Message, self).__init__(**kwargs)


class Scalar(Message):
    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)


class Resource(Message):
    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)


# TODO: RangeResource e.g. ports
class ScalarResource(Resource):
    def __init__(self, value=None, **kwargs):
        super(Resource, self).__init__(**kwargs)
        if value is not None:
            self.scalar = Scalar(value=value)

    def __eq__(self, second):
        first, second = float(self), float(second)
        return not first < second and not second < first

    def __ne__(self, second):
        first, second = float(self), float(second)
        return self < second or second < first

    def __gt__(self, second):
        first, second = float(self), float(second)
        return second < first

    def __ge__(self, second):
        first, second = float(self), float(second)
        return not first < second

    def __le__(self, second):
        first, second = float(self), float(second)
        return not second < first

    def __lt__(self, second):
        first, second = float(self), float(second)
        return first < second

    def __repr__(self):
        return "<{}: {}>".format(self.__class__.__name__, self.scalar.value)

    def __float__(self):
        return float(self.scalar.value)

    @classmethod
    def _op(cls, op, first, second):
        value = op(float(first), float(second))
        return cls(value=value)

    def __add__(self, second):
        return self._op(operator.add, self, second)

    def __radd__(self, second):
        return self._op(operator.add, second, self)

    def __sub__(self, second):
        return self._op(operator.sub, self, second)

    def __rsub__(self, second):
        return self._op(operator.sub, second, self)

    def __mul__(self, second):
        return self._op(operator.mul, self, second)

    def __rmul__(self, second):
        return self._op(operator.mul, second, self)

    def __truediv__(self, second):
        return self._op(operator.truediv, self, second)

    def __rtruediv__(self, second):
        return self._op(operator.truediv, second, self)

    def __iadd__(self, second):
        self.scalar.value = float(self._op(operator.add, self, second))
        return self

    def __isub__(self, second):
        self.scalar.value = float(self._op(operator.sub, self, second))
        return self


class Cpus(ScalarResource):
    def __init__(self, value):
        super(Cpus, self).__init__(value=value, name="cpus", type="SCALAR")


class Mem(ScalarResource):
    def __init__(self, value):
        super(Mem, self).__init__(value=value, name="mem", type="SCALAR")


class Disk(ScalarResource):
    def __init__(self, value):
        super(Disk, self).__init__(value=value, name="disk", type="SCALAR")


class ResourcesMixin(object):
    @classmethod
    def _cast_zero(cls, second=0):
        if second == 0:
            return cls(resources=[Cpus(0), Mem(0), Disk(0)])
        else:
            return second

    @property
    def cpus(self):
        for res in self.resources:
            if res.name == "cpus":
                return Cpus(res.scalar.value)
        return Cpus(0.0)

    @property
    def mem(self):
        for res in self.resources:
            if res.name == "mem":
                return Mem(res.scalar.value)
        return Mem(0.0)

    @property
    def disk(self):
        for res in self.resources:
            if res.name == "disk":
                return Disk(res.scalar.value)
        return Disk(0.0)

    # @property
    # def ports(self):
    #     for res in self.resources:
    #         if isinstance(res, Ports):
    #             return [(rng.begin, rng.end) for rng in res.ranges.range]

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__,
                                 ', '.join(map(str, self.resources)))

    def __eq__(self, second):
        second = self._cast_zero(second)
        return all([self.cpus == second.cpus,
                    self.mem == second.mem,
                    self.disk == second.disk])

    def __ne__(self, second):
        second = self._cast_zero(second)
        return all([self.cpus != second.cpus,
                    self.mem != second.mem,
                    self.disk != second.disk])

    def __gt__(self, second):
        second = self._cast_zero(second)
        return any([self.cpus > second.cpus,
                    self.mem > second.mem,
                    self.disk > second.disk])

    def __ge__(self, second):
        second = self._cast_zero(second)
        return any([self.cpus >= second.cpus,
                    self.mem >= second.mem,
                    self.disk >= second.disk])

    def __le__(self, second):
        second = self._cast_zero(second)
        return all([self.cpus <= second.cpus,
                    self.mem <= second.mem,
                    self.disk <= second.disk])

    def __lt__(self, second):
        second = self._cast_zero(second)
        return all([self.cpus < second.cpus,
                    self.mem < second.mem,
                    self.disk < second.disk])

    def __radd__(self, second):  # to support sum()
        second = self._cast_zero(second)
        return self + second

    def __add__(self, second):
        second = self._cast_zero(second)
        # ports = list(set(self.ports) | set(second.ports))
        cpus = self.cpus + second.cpus
        mem = self.mem + second.mem
        disk = self.disk + second.disk
        mixin = self.__class__()
        mixin.resources = [cpus, disk, mem]
        return mixin

    def __sub__(self, second):
        second = self._cast_zero(second)
        # ports = list(set(self.ports) | set(second.ports))
        cpus = self.cpus - second.cpus
        mem = self.mem - second.mem
        disk = self.disk - second.disk
        mixin = self.__class__()
        mixin.resources = [cpus, disk, mem]
        return mixin

    def __iadd__(self, second):
        second = self._cast_zero(second)
        added = self + second
        self.resources = added.resources
        return self

    def __isub__(self, second):
        second = self._cast_zero(second)
        subbed = self - second
        self.resources = subbed.resources
        return self


class FrameworkID(Message):
    def __init__(self, **kwargs):
        if "value" not in kwargs:
            raise AttributeError
        super(FrameworkID, self).__init__(**kwargs)


class SlaveID(Message):
    def __init__(self, **kwargs):
        if "value" not in kwargs:
            raise AttributeError
        super(SlaveID, self).__init__(**kwargs)


class ExecutorID(Message):
    def __init__(self, **kwargs):
        if "value" not in kwargs:
            raise AttributeError
        super(ExecutorID, self).__init__(**kwargs)


class AgentID(Message):
    def __init__(self, **kwargs):
        if "value" not in kwargs:
            raise AttributeError
        super(AgentID, self).__init__(**kwargs)


class OfferID(Message):
    def __init__(self, **kwargs):
        if "value" not in kwargs:
            raise AttributeError
        super(OfferID, self).__init__(**kwargs)


class TaskID(Message):
    def __init__(self, **kwargs):
        if "value" not in kwargs:
            raise AttributeError
        super(TaskID, self).__init__(**kwargs)


class AgentInfo(Message):
    pass


class FrameworkInfo(Message):
    pass


class ExecutorInfo(Message):
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


class MasterInfo(Message):
    pass


class SlaveInfo(Message):
    pass


class Filters(Message):
    pass


class TaskStatus(Message):
    def __init__(self, **kwargs):
        super(TaskStatus, self).__init__(**kwargs)

    @property
    def task_id(self):  # more consistent naming
        return self['task_id']

    @task_id.setter
    def task_id(self, value):
        if not isinstance(value, TaskID):
            value = TaskID(value=value) if not isinstance(value, dict) else  TaskID(**value)
        self['task_id'] = value

    def is_staging(self):
        return self.state == 'TASK_STAGING'

    def is_starting(self):
        return self.state == 'TASK_STARTING'

    def is_running(self):
        return self.state == 'TASK_RUNNING'

    def has_finished(self):
        return self.state == 'TASK_FINISHED'

    def has_succeeded(self):
        return self.state == 'TASK_FINISHED'

    def has_killed(self):
        return self.state == 'TASK_KILLED'

    def has_failed(self):
        return self.state in ['TASK_FAILED', 'TASK_LOST', 'TASK_KILLED',
                              'TASK_ERROR']

    def has_terminated(self):
        return self.has_succeeded() or self.has_failed()


class Offer(ResourcesMixin, Message):  # important order!
    def __init__(self, **kwargs):
        super(Offer, self).__init__(**kwargs)

    @property
    def framework_id(self):
        return self['framework_id']

    @framework_id.setter
    def framework_id(self, value):
        if not isinstance(value, (FrameworkID)):
            value = FrameworkID(value=value) if not isinstance(value, dict) else  FrameworkID(**value)
        self['framework_id'] = value

    @property
    def agent_id(self):
        return self['agent_id']

    @agent_id.setter
    def agent_id(self, value):
        if not isinstance(value, (AgentID, SlaveID)):
            value = AgentID(value=value) if not isinstance(value, dict) else  AgentID(**value)
        self['agent_id'] = value

    @property
    def id(self):
        return self['id']

    @id.setter
    def id(self, value):
        if not isinstance(value, (OfferID)):
            value = OfferID(value=value) if not isinstance(value, dict) else  OfferID(**value)
        self['id'] = value

    @property
    def slave_id(self):
        return self['agent_id']

    @slave_id.setter
    def slave_id(self, value):
        if not isinstance(value, (AgentID, SlaveID)):
            value = AgentID(value=value) if not isinstance(value, dict) else  AgentID(**value)
        self['agent_id'] = value


class TaskInfo(ResourcesMixin, Message):
    def __init__(self, task_id=None, **kwargs):
        super(TaskInfo, self).__init__(**kwargs)
        self.task_id = task_id or str(uuid4())
        self.status = TaskStatus(task_id=self.task_id, state='TASK_STAGING')

    # @property
    # def id(self):  # more consistent naming
    #     return self['task_id']
    #
    # @id.setter
    # def id(self, value):
    #     if not isinstance(value, TaskID):
    #         value = TaskID(value=value)
    #     self['task_id'] = value

    @property
    def slave_id(self):
        return self['agent_id']

    @slave_id.setter
    def slave_id(self, value):
        if not isinstance(value, (AgentID, SlaveID)):
            value = AgentID(value=value)
        self['agent_id'] = value


class CommandInfo(Message):
    pass


class ContainerInfo(Message):
    pass

    class DockerInfo(Message):
        pass

    class MesosInfo(Message):
        pass


class Image(Message):
    pass

    class Appc(Message):
        pass

    class Docker(Message):
        pass


class Request(Message):
    pass


class Operation(Message):
    pass

class DockerInfo(Message):
    pass