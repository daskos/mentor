from __future__ import absolute_import, division, print_function

import operator
import types
import attr
from uuid import uuid4
from functools import total_ordering
from mentor.messages.message import Message

class Scalar(Message):
    key = 'scalar'


class Resource(Message):
    key = "resources"



class ScalarResource(Resource):
    key = 'scalar_resource'
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


class ResourcesMixin(object):
    key = "disk"
    @classmethod
    def _cast_zero(cls, second=0):
        if second == 0:
            return cls.encode(dict(resources=[Cpus(0), Mem(0), Disk(0)]))
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


class Cpus(ScalarResource):
    key = "cpus"
    def __init__(self, value=None,**kwargs):
        super(Cpus, self).__init__(value,**kwargs)
        self.name = "cpus"
        self.type = "SCALAR"


class Mem(ScalarResource):
    key = "mem"
    def __init__(self, value=None,**kwargs):
        super(Mem, self).__init__(value,**kwargs)
        self.name = "mem"
        self.type = "SCALAR"


class Disk(ScalarResource):
    key = "disk"
    def __init__(self, value=None,**kwargs):
        super(Disk, self).__init__(value,**kwargs)
        self.name = "disk"
        self.type = "SCALAR"


class Offer(ResourcesMixin,Message):
    key = "offer"
    pass



class TaskStatus(Message):
    key = "task_status"
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




class TaskInfo(ResourcesMixin,Message):
    key = "task_info"
    def __init__(self,*args):
        super(TaskInfo, self).__init__(*args)
        self.id = self.get("task_id" ,str(uuid4()))
        self.status = TaskStatus.encode(dict(task_id=self.id, state='TASK_STAGING'))

    @property
    def id(self):  # more consistent naming
        return self.get('task_id',None)

    @id.setter
    def id(self, value):
        if not isinstance(value, dict):
            value = dict(value=value)
        self['task_id'] = value


res=[{'name': 'cpus', 'type': 'SCALAR', 'scalar': {'value': 0.2}}, {'name': 'mem', 'type': 'SCALAR', 'scalar': {'value': 128}}]

task_info = {'task_id': {'value': '39e762f5-9767-4d7d-b187-67029df5b151'}, 'agent_id': {'value': '7037ef03-cbef-4e11-aac6-d662a5ef4179-S1'}, 'name': 'task 39e762f5-9767-4d7d-b187-67029df5b151', 'executor': {'executor_id': {'value': 'MinimalExecutor'}, 'name': 'MinimalExecutor', 'command': {'value': '/opt/anaconda3/envs/mentos/bin/python /home/arti/workdir/mesos/dmentos/examples/executor.py'}, 'resources': [{'name': 'mem', 'type': 'SCALAR', 'scalar': {'value': 32}}, {'name': 'cpus', 'type': 'SCALAR', 'scalar': {'value': 0.1}}]}, 'data': 'SGVsbG8gZnJvbSB0YXNrIDM5ZTc2MmY1LTk3NjctNGQ3ZC1iMTg3LTY3MDI5ZGY1YjE1MSE=', 'resources': [{'name': 'cpus', 'type': 'SCALAR', 'scalar': {'value': 0.2}}, {'name': 'mem', 'type': 'SCALAR', 'scalar': {'value': 128}}]}

TaskInfo.encode(task_info) + TaskInfo.encode(task_info)
a=1
pass