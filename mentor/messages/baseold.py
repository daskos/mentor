from __future__ import absolute_import, division, print_function

import operator
import types
import attr
from uuid import uuid4


defaults ={
    type(float()):0.0,
    type(int()): 0,
    type(str()): "",
    type(bool()): False

}


def message(cls,is_list=False, default=None, validator=None, repr=True, cmp=True, hash=True, init=True, convert=None):

    def convert(d):
        return cls(**d) if type(d) == type(dict()) else d if d else defaults[cls] if cls in  defaults else None

    if is_list:
        def convert_f(d):
          return [convert(v) for v in d]
        if default == None:
           default = attr.Factory(list)
    else:
        convert_f = convert



    return attr.ib(default=default, validator=validator,repr= repr,cmp=cmp,hash= hash, init=init, convert=convert_f)



@attr.s(cmp=False)
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



@attr.s(cmp=False)
class Scalar(object):
    value = message(float)

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
        return "<{}: {}>".format(self.__class__.__name__, self.value)

    def __float__(self):
        return float(self.value)

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
        self.value = float(self._op(operator.add, self, second))
        return self

    def __isub__(self, second):
        self.value = float(self._op(operator.sub, self, second))
        return self

@attr.s
class Range(object):
        begin = message(int)
        end = message(int)

@attr.s
class Parameter(object):
    key = message(str)

    value = message(str)

@attr.s
class Set(object):
    item = message(str)


@attr.s
class Address(object):
                hostname = message(str)
                ip = message(str)
                port = message(int)
@attr.s
class URL(object):
                fragment = message(str)
                path = message(str)
                query = message(Parameter)
                scheme = message(str)
                address = message(Address, is_list=True)

class Text(object):
    value = message(str)


@attr.s
class Attribute(object):
                name = message(str)
                scalar = message(Scalar)
                set = message(Set)
                text = message(Text)
                type = message(object)
                ranges = message(Range, is_list=True)

@attr.s
class DurationInfo(object):
                nanoseconds =  message(int)

@attr.s
class TimeInfo(object):
                nanoseconds =  message(int)

@attr.s
class Unavailability(object):
                duration = message(DurationInfo)
                start = message(TimeInfo)

@attr.s
class Label(object):
    key = message(str)

    value = message(str)


@attr.s
class ReservationInfo(object):

    principal = message(str)
    labels = message(Label, is_list=True)


@attr.s
class Persistence(object):
    id = message(str)

    principal = message(str)



@attr.s
class Mount(object):
    root = message(str)


@attr.s
class Path(object):
    root = message(str)



@attr.s
class Source(object):
    mount = message(Mount)

    path = message(Path)

    type = message(str)


@attr.s
class Credential(object):
    principal = message(str)
    secret = message(str)


@attr.s
class Appc(object):
    id = message(str)
    name = message(str)
    labels = message(Label, is_list=True)


@attr.s
class Docker(object):
    credential = message(Credential)
    name = message(str)


@attr.s
class Image(object):
    type = message(str)
    appc = message(Appc)
    cached = message(bool)
    docker = message(Docker)



@attr.s
class Volume(object):
    container_path = message(str)
    host_path = message(str)
    image = message(Image)
    mode = message(str)
    source = message(Source)





@attr.s
class DiskInfo(object):
    persistence = message(Persistence)
    source = message(Source)
    volume = message(Volume)






@attr.s
class ExecutorID(object):
    value = message(str)

@attr.s
class FrameworkID(object):
    value = message(str)

@attr.s
class OfferID(object):
    value = message(str)

@attr.s
class AgentID(object):
    value = message(str)

@attr.s
class TaskID(object):
    value = message(str)



@attr.s
class Resource(object):
       disk = message(DiskInfo)
       name = message(str)
       reservation = message(ReservationInfo)
       revocable = message(object)
       role = message(str)
       scalar = message(Scalar)
       set = message(Set)
       shared = message(object)
       type = message(object)
       ranges = message(Range, is_list=True)



@attr.s(cmp=False)
class Offer(ResourcesMixin):
       framework_id = message(FrameworkID)
       hostname = message(str)
       id = message(OfferID)
       agent_id = message(AgentID)
       unavailability = message(Unavailability)
       url = message(URL)
       resources = message(Resource, is_list=True)
       attributes = message(Attribute, is_list=True)
       executor_ids = message(ExecutorID, is_list=True)

@attr.s(cmp=False)
class Cpus(Scalar):
    name = "cpus"
    type = "SCALAR"

    @property
    def scalar(self):
        return self


@attr.s(cmp=False)
class Mem(Scalar):
    name = "mem"
    type = "SCALAR"

    @property
    def scalar(self):
        return self


@attr.s(cmp=False)
class Disk(Scalar):
    name = "disk"
    type = "SCALAR"

    @property
    def scalar(self):
        return self

