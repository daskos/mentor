from __future__ import absolute_import, division, print_function

import operator

import attr
from uuid import uuid4

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
    value = attr.ib(default=None)

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
class Variable(object):
    name = attr.ib(None)
    value = attr.ib(None)


@attr.s
class Environment(object):
    variables = attr.ib(default=attr.Factory(list), convert=lambda d: [Variable(**v)  if type(d) == type(dict()) else d if d else None for v in d])


@attr.s
class DiscoveryInfo(object):
    environment = attr.ib(default=None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    location = attr.ib(default=None)

    name = attr.ib(default=None)

    ports = attr.ib(default=None, convert=lambda d: Ports(**d) if type(d) == type(dict()) else d if d else None)

    version = attr.ib(default=None)

    visibility = attr.ib(default=None)


@attr.s
class Task(object):
    id = attr.ib(default=None, convert=lambda d: TaskID(**d) if type(d) == type(dict()) else d if d else None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)
    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class DurationInfo(object):
    nanoseconds = attr.ib(default=None)


@attr.s(cmp=False)
class Offer(ResourcesMixin):
    attributes = attr.ib(default=attr.Factory(list),
                         convert=lambda d: [Attribute(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    executor_ids = attr.ib(default=attr.Factory(list),
                        convert=lambda d: [ExecutorID(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    framework_id = attr.ib(default=None,
                           convert=lambda d: FrameworkID(**d) if type(d) == type(dict()) else d if d else None)

    hostname = attr.ib(default=None)

    id = attr.ib(default=None, convert=lambda d: OfferID(**d) if type(d) == type(dict()) else d if d else None)

    resources = attr.ib(default=attr.Factory(list), convert=lambda v: [Resource(**d) if type(d) == type(dict()) else d if d else None for d in v])

    agent_id = attr.ib(default=None, convert=lambda d: AgentID(**d) if type(d) == type(dict()) else d if d else None)

    unavailability = attr.ib(default=None,
                             convert=lambda d: Unavailability(**d) if type(d) == type(dict()) else d if d else None)

    url = attr.ib(default=None, convert=lambda d: URL(**d) if type(d) == type(dict()) else d if d else None)



@attr.s
class TCPCheckInfo(object):
    port = attr.ib(default=None)


@attr.s
class HTTPCheckInfo(object):
    port = attr.ib(default=None)


@attr.s
class HealthCheck(object):
    command = attr.ib(default=None, convert=lambda d: CommandInfo(**d) if type(d) == type(dict()) else d if d else None)

    consecutive_failures = attr.ib(default=None)

    delay_seconds = attr.ib(default=None)

    grace_period_seconds = attr.ib(default=None)

    http = attr.ib(default=None, convert=lambda d: HTTPCheckInfo(**d) if type(d) == type(dict()) else d if d else None)

    interval_seconds = attr.ib(default=None)

    tcp = attr.ib(default=None, convert=lambda d: TCPCheckInfo(**d) if type(d) == type(dict()) else d if d else None)

    timeout_seconds = attr.ib(default=None)

    type = attr.ib(default=None)


@attr.s
class Port(object):
    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)

    number = attr.ib(default=None)

    protocol = attr.ib(default=None)

    visibility = attr.ib(default=None)


@attr.s
class URL(object):
    address = attr.ib(default=None, convert=lambda d: Address(**d) if type(d) == type(dict()) else d if d else None)

    fragment = attr.ib(default=None)

    path = attr.ib(default=None)

    query = attr.ib(default=None, convert=lambda d: Parameter(**d) if type(d) == type(dict()) else d if d else None)

    scheme = attr.ib(default=None)


@attr.s
class IPAddress(object):
    protocol = attr.ib(default=None)
    ip_address = attr.ib(default=None)


@attr.s
class PortMapping(object):
    container_port = attr.ib(default=None)

    host_port = attr.ib(default=None)

    protocol = attr.ib(default=None)


@attr.s
class NetworkInfo(object):
    groups = attr.ib(default=attr.Factory(list))

    ip_addresses = attr.ib(default=attr.Factory(list),
                          convert=lambda d: [ IPAddress(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)

    port_mappings = attr.ib(default=None,
                            convert=lambda d: PortMapping(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class MasterInfo(object):
    address = attr.ib(default=None, convert=lambda d: Address(**d) if type(d) == type(dict()) else d if d else None)

    hostname = attr.ib(default=None)

    id = attr.ib(default=None)

    ip = attr.ib(default=None)

    pid = attr.ib(default=None)

    port = attr.ib(default=None)

    version = attr.ib(default=None)


@attr.s
class Unavailability(object):
    duration = attr.ib(default=None,
                       convert=lambda d: DurationInfo(**d) if type(d) == type(dict()) else d if d else None)

    start = attr.ib(default=None, convert=lambda d: TimeInfo(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class InverseOffer(object):
    framework_id = attr.ib(default=None,
                           convert=lambda d: FrameworkID(**d) if type(d) == type(dict()) else d if d else None)

    id = attr.ib(default=None, convert=lambda d: OfferID(**d) if type(d) == type(dict()) else d if d else None)

    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)

    agent_id = attr.ib(default=None, convert=lambda d: AgentID(**d) if type(d) == type(dict()) else d if d else None)

    unavailability = attr.ib(default=None,
                             convert=lambda d: Unavailability(**d) if type(d) == type(dict()) else d if d else None)

    url = attr.ib(default=None, convert=lambda d: URL(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class Capability(object):
    type = attr.ib(default=None)


@attr.s
class FrameworkInfo(object):
    capabilities = attr.ib(default=attr.Factory(list), convert=lambda d: [Capability(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    checkpoint = attr.ib(default=None)

    failover_timeout = attr.ib(default=None)

    hostname = attr.ib(default=None)

    id = attr.ib(default=None, convert=lambda d: FrameworkID(**d) if type(d) == type(dict()) else d if d else None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)

    principal = attr.ib(default=None)

    role = attr.ib(default=None)

    user = attr.ib(default=None)

    webui_url = attr.ib(default=None)


@attr.s
class Labels(object):
    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class NetCls(object):
    classid = attr.ib(default=None)


@attr.s
class CgroupInfo(object):
    net_cls = attr.ib(default=None, convert=lambda d: NetCls(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class TaskStatus(object):
    container_status = attr.ib(default=None,
                               convert=lambda d: ContainerStatus(**d) if type(d) == type(dict()) else d if d else None)

    data = attr.ib(default=None)

    executor_id = attr.ib(default=None,
                          convert=lambda d: ExecutorID(**d) if type(d) == type(dict()) else d if d else None)

    healthy = attr.ib(default=None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    message = attr.ib(default=None)

    reason = attr.ib(default=None)

    agent_id = attr.ib(default=None, convert=lambda d: AgentID(**d) if type(d) == type(dict()) else d if d else None)

    source = attr.ib(default=None)

    state = attr.ib(default=None)

    task_id = attr.ib(default=None, convert=lambda d: TaskID(**d) if type(d) == type(dict()) else d if d else None)

    timestamp = attr.ib(default=None)

    unreachable_time = attr.ib(default=None,
                               convert=lambda d: TimeInfo(**d) if type(d) == type(dict()) else d if d else None)

    uuid = attr.ib(default=None)

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


@attr.s
class WeightInfo(object):
    role = attr.ib(default=None)

    weight = attr.ib(default=None)


@attr.s
class Parameter(object):
    key = attr.ib(default=None)

    value = attr.ib(default=None)


@attr.s(cmp=False)
class TaskInfo(ResourcesMixin):
    command = attr.ib(default=None, convert=lambda d: CommandInfo(**d) if type(d) == type(dict()) else d if d else None)

    container = attr.ib(default=None,
                        convert=lambda d: ContainerInfo(**d) if type(d) == type(dict()) else d if d else None)

    data = attr.ib(default=None)

    discovery = attr.ib(default=None,
                        convert=lambda d: DiscoveryInfo(**d) if type(d) == type(dict()) else d if d else None)

    executor = attr.ib(default=attr.Factory(list),
                       convert=lambda d: [ ExecutorInfo(**v)  if type(d) == type(dict()) else d if d else None for  v in d])

    health_check = attr.ib(default=None,
                           convert=lambda d: HealthCheck(**d) if type(d) == type(dict()) else d if d else None)

    kill_policy = attr.ib(default=None,
                          convert=lambda d: KillPolicy(**d) if type(d) == type(dict()) else d if d else None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)

    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)

    agent_id = attr.ib(default=None, convert=lambda d: AgentID(**d) if type(d) == type(dict()) else d if d else None)

    task_id = attr.ib(default={"value":str(uuid4())}, convert=lambda d: TaskID(**d) if type(d) == type(dict()) else d if d else None)

    status = TaskStatus(task_id=task_id, state='TASK_STAGING')

    @property
    def id(self):  # more consistent naming
        return self.task_id

    @id.setter
    def id(self, value):
        self.task_id = id

    @property
    def agent_id(self):
        return self.agent_id

    @agent_id.setter
    def agent_id(self, value):
        self.agent_id = value


@attr.s()
class TaskGroupInfo():
     tasks = attr.ib(default=attr.Factory(list), convert=lambda d: [ TaskInfo(**v)  if type(d) == type(dict()) else d if d else None for v in d])

@attr.s
class Request(object):
    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)

    agent_id = attr.ib(default=None, convert=lambda d: AgentID(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class LinuxInfo(object):
    capability_info = attr.ib(default=None,
                              convert=lambda d: CapabilityInfo(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class ExecutorInfo(object):
    command = attr.ib(default=None, convert=lambda d: CommandInfo(**d) if type(d) == type(dict()) else d if d else None)

    container = attr.ib(default=None,
                        convert=lambda d: ContainerInfo(**d) if type(d) == type(dict()) else d if d else None)

    data = attr.ib(default=None)

    discovery = attr.ib(default=None,
                        convert=lambda d: DiscoveryInfo(**d) if type(d) == type(dict()) else d if d else None)

    executor_id = attr.ib(default=None,
                          convert=lambda d: ExecutorID(**d) if type(d) == type(dict()) else d if d else None)

    framework_id = attr.ib(default=None,
                           convert=lambda d: FrameworkID(**d) if type(d) == type(dict()) else d if d else None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)

    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)

    shutdown_grace_period = attr.ib(default=None, convert=lambda d: DurationInfo(**d) if type(d) == type(
        dict()) else d if d else None)

    source = attr.ib(default=None)

    type = attr.ib(default=None)


@attr.s
class Filters(object):
    refuse_seconds = attr.ib(default=None)


@attr.s
class Flag(object):
    name = attr.ib(default=None)

    value = attr.ib(default=None)


@attr.s
class Mount(object):
    root = attr.ib(default=None)


@attr.s
class Path(object):
    root = attr.ib(default=None)


@attr.s
class Persistence(object):
    id = attr.ib(default=None)

    principal = attr.ib(default=None)


@attr.s
class Source(object):
    mount = attr.ib(default=None, convert=lambda d: Mount(**d) if type(d) == type(dict()) else d if d else None)

    path = attr.ib(default=None, convert=lambda d: Path(**d) if type(d) == type(dict()) else d if d else None)

    type = attr.ib(default=None)


@attr.s
class ReservationInfo(object):
    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    principal = attr.ib(default=None)


@attr.s
class DiskInfo(object):
    persistence = attr.ib(default=None,
                          convert=lambda d: Persistence(**d) if type(d) == type(dict()) else d if d else None)

    source = attr.ib(default=None, convert=lambda d: Source(**d) if type(d) == type(dict()) else d if d else None)

    volume = attr.ib(default=None, convert=lambda d: Volume(**d) if type(d) == type(dict()) else d if d else None)


@attr.s(cmp=False)
class Cpus(Scalar):
    name = "cpus"
    type = "SCALAR"

    @property
    def scalar(self):
        return self


@attr.s(cmp=False)
class Mem(Scalar):
    # scalar = attr.ib(default=None,convert=lambda d: Scalar(d))
    name = "mem"
    type = "SCALAR"

    @property
    def scalar(self):
        return self


@attr.s(cmp=False)
class Disk(Scalar):
    # scalar = attr.ib(default=None,convert=lambda d: Scalar(d))
    name = "disk"
    type = "SCALAR"

    @property
    def scalar(self):
        return self


@attr.s
class Resource(object):
    disk = attr.ib(default=None, convert=lambda d: DiskInfo(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)

    ranges = attr.ib(default=None, convert=lambda d: Ranges(**d) if type(d) == type(dict()) else d if d else None)

    reservation = attr.ib(default=None,
                          convert=lambda d: ReservationInfo(**d) if type(d) == type(dict()) else d if d else None)

    revocable = attr.ib(default=None)

    role = attr.ib(default=None)

    scalar = attr.ib(default=None, convert=lambda d: Scalar(**d) if type(d) == type(dict()) else d if d else None)

    set = attr.ib(default=None, convert=lambda d: Set(**d) if type(d) == type(dict()) else d if d else None)

    shared = attr.ib(default=None)

    type = attr.ib(default=None)


@attr.s
class ExecutorID(object):
    value = attr.ib(default=None)


@attr.s
class Set(object):
    item = attr.ib(default=attr.Factory(set))


@attr.s
class Ranges(object):
    range = attr.ib(default=attr.Factory(list), convert=lambda d:  [Range(**v)  if type(d) == type(dict()) else d if d else None for v in d])


@attr.s
class Range(object):
    begin = attr.ib(default=None)

    end = attr.ib(default=None)


@attr.s
class Text(object):
    value = attr.ib(default=None)


@attr.s
class Attribute(object):
    name = attr.ib(default=None)

    ranges = attr.ib(default=None, convert=lambda d: Ranges(**d) if type(d) == type(dict()) else d if d else None)

    scalar = attr.ib(default=None, convert=lambda d: Scalar(**d) if type(d) == type(dict()) else d if d else None)

    set = attr.ib(default=None, convert=lambda d: Set(**d) if type(d) == type(dict()) else d if d else None)

    text = attr.ib(default=None, convert=lambda d: Text(**d) if type(d) == type(dict()) else d if d else None)

    type = attr.ib(default=None)


@attr.s
class Volume(object):
    container_path = attr.ib(default=None)

    host_path = attr.ib(default=None)

    image = attr.ib(default=None, convert=lambda d: Image(**d) if type(d) == type(dict()) else d if d else None)

    mode = attr.ib(default=None)

    source = attr.ib(default=None, convert=lambda d: Source(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class ContainerStatus(object):
    cgroup_info = attr.ib(default=None,
                          convert=lambda d: CgroupInfo(**d) if type(d) == type(dict()) else d if d else None)

    executor_pid = attr.ib(default=None)

    network_infos = attr.ib(default=None,
                            convert=lambda d: NetworkInfo(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class SlaveInfo(object):
    attributes = attr.ib(default=attr.Factory(list),
                       convert=lambda d: [Attribute(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    checkpoint = attr.ib(default=None)

    hostname = attr.ib(default=None)

    id = attr.ib(default=None, convert=lambda d: AgentID(**d) if type(d) == type(dict()) else d if d else None)

    port = attr.ib(default=None)

    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class CommandInfo(object):
    arguments = attr.ib(default=attr.Factory(list))

    environment = attr.ib(default=None,
                          convert=lambda d: Environment(**d) if type(d) == type(dict()) else d if d else None)

    shell = attr.ib(default=None)

    uris = attr.ib(default=attr.Factory(list), convert=lambda d: URI(**d)  if type(d) == type(dict()) else d if d else None)

    user = attr.ib(default=None)

    value = attr.ib(default=None)


@attr.s
class Appc(object):
    id = attr.ib(default=None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)


@attr.s
class Docker(object):
    credential = attr.ib(default=None,
                         convert=lambda d: Credential(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)


@attr.s
class Image(object):
    type = attr.ib(default=None)
    appc = attr.ib(default=None, convert=lambda d: Appc(**d) if type(d) == type(dict()) else d if d else None)

    cached = attr.ib(default=None)

    docker = attr.ib(default=None, convert=lambda d: Docker(**d) if type(d) == type(dict()) else d if d else None)




@attr.s
class URI(object):
    cache = attr.ib(default=None)

    executable = attr.ib(default=None)

    extract = attr.ib(default=None)

    output_file = attr.ib(default=None)

    value = attr.ib(default=None)


@attr.s
class TaskGroupInfo(object):
    tasks = attr.ib(default=None, convert=lambda d: TaskInfo(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class RateLimit(object):
    capacity = attr.ib(default=None)

    principal = attr.ib(default=None)

    qps = attr.ib(default=None)


@attr.s
class Value(object):
    ranges = attr.ib(default=None, convert=lambda d: Ranges(**d) if type(d) == type(dict()) else d if d else None)

    scalar = attr.ib(default=None, convert=lambda d: Scalar(**d) if type(d) == type(dict()) else d if d else None)

    set = attr.ib(default=None, convert=lambda d: Set(**d) if type(d) == type(dict()) else d if d else None)

    text = attr.ib(default=None, convert=lambda d: Text(**d) if type(d) == type(dict()) else d if d else None)

    type = attr.ib(default=None)


@attr.s
class OfferID(object):
    value = attr.ib(default=None)


@attr.s
class Ports(object):
    ports = attr.ib(default=attr.Factory(list), convert=lambda d:  [Port(**v)  if type(d) == type(dict()) else d if d else None for v in d])


@attr.s
class AgentID(object):
    value = attr.ib(default=None)


@attr.s
class ContainerInfo(object):
    @attr.s
    class DockerInfo(object):
        force_pull_image = attr.ib(default=None)

        image = attr.ib(default=None)

        network = attr.ib(default=None)

        parameters = attr.ib(default=attr.Factory(list), convert=lambda d:  [Parameter(**v)  if type(d) == type(dict()) else d if d else None for v in d])

        port_mappings = attr.ib(default=attr.Factory(list), convert=lambda d:  [PortMapping(**v)  if type(d) == type(dict()) else d if d else None for v in d])

        privileged = attr.ib(default=None)

        volume_driver = attr.ib(default=None)

    @attr.s
    class MesosInfo(object):
        image = attr.ib(default=None, convert=lambda d: Image(**d) if type(d) == type(dict()) else d if d else None)

    docker = attr.ib(default=None,
                     convert=lambda d: ContainerInfo.DockerInfo(**d) if type(d) == type(dict()) else d if d else None)

    hostname = attr.ib(default=None)

    linux_info         = attr.ib(default=None,
                         convert=lambda d: LinuxInfo(**d) if type(d) == type(dict()) else d if d else None)

    mesos = attr.ib(default=None,
                    convert=lambda d: ContainerInfo.MesosInfo(**d) if type(d) == type(dict()) else d if d else None)

    network_infos = attr.ib(default=attr.Factory(list), convert=lambda d:  [NetworkInfo(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    type = attr.ib(default=None)

    volumes = attr.ib(default=attr.Factory(list), convert=lambda d:  [Volume(**v)  if type(d) == type(dict()) else d if d else None for v in d])


@attr.s
class KillPolicy(object):
    grace_period = attr.ib(default=None,
                           convert=lambda d: DurationInfo(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class Address(object):
    hostname = attr.ib(default=None)

    ip = attr.ib(default=None)

    port = attr.ib(default=None)


@attr.s
class CapabilityInfo(object):
    capabilities = attr.ib(default=attr.Factory(list))


@attr.s
class MachineID(object):
    hostname = attr.ib(default=None)

    ip = attr.ib(default=None)


@attr.s
class TimeInfo(object):
    nanoseconds = attr.ib(default=None)


@attr.s
class MachineInfo(object):
    id = attr.ib(default=None, convert=lambda d: MachineID(**d) if type(d) == type(dict()) else d if d else None)

    mode = attr.ib(default=None)

    unavailability = attr.ib(default=None,
                             convert=lambda d: Unavailability(**d) if type(d) == type(dict()) else d if d else None)


@attr.s
class Parameters(object):
    parameter = attr.ib(default=attr.Factory(list), convert=lambda d: [Parameter(**v)  if type(d) == type(dict()) else d if d else None for v in d ])


@attr.s
class Task(object):
    container = attr.ib(default=None,
                        convert=lambda d: ContainerInfo(**d) if type(d) == type(dict()) else d if d else None)

    discovery = attr.ib(default=None,
                        convert=lambda d: DiscoveryInfo(**d) if type(d) == type(dict()) else d if d else None)

    executor_id = attr.ib(default=None,
                          convert=lambda d: ExecutorID(**d) if type(d) == type(dict()) else d if d else None)

    framework_id = attr.ib(default=None,
                           convert=lambda d: FrameworkID(**d) if type(d) == type(dict()) else d if d else None)

    labels = attr.ib(default=None, convert=lambda d: Labels(**d) if type(d) == type(dict()) else d if d else None)

    name = attr.ib(default=None)

    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)

    agent_id = attr.ib(default=None, convert=lambda d: AgentID(**d) if type(d) == type(dict()) else d if d else None)

    state = attr.ib(default=None)

    status_update_state = attr.ib(default=None)

    status_update_uuid = attr.ib(default=None)

    statuses = attr.ib(default=attr.Factory(list), convert=lambda d: [TaskStatus(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    task_id = attr.ib(default={"value":str(uuid4())}, convert=lambda d: TaskID(**d) if type(d) == type(dict()) else d if d else None)

    user = attr.ib(default=None)


@attr.s
class ContainerID(object):
    parent = attr.ib(default=None, convert=lambda d: ContainerID(**d) if type(d) == type(dict()) else d if d else None)

    value = attr.ib(default=None)


@attr.s
class Label(object):
    key = attr.ib(default=None)

    value = attr.ib(default=None)


@attr.s
class Credentials(object):
    credentials = attr.ib(default=attr.Factory(list),
                          convert=lambda d: [ Credential(**v)  if type(d) == type(dict()) else d if d else None for v in d])


@attr.s
class Role(object):
    frameworks = attr.ib(default=attr.Factory(list), convert=lambda d:  [FrameworkID(**v)  if type(d) == type(dict()) else d if d else None for v in d])

    name = attr.ib(default=None)

    resources = attr.ib(default=None, convert=lambda d: Resource(**d) if type(d) == type(dict()) else d if d else None)

    weight = attr.ib(default=None)


@attr.s
class FrameworkID(object):
    value = attr.ib(default=None)


@attr.s
class TaskID(object):
    value = attr.ib(default=None)


@attr.s
class Credential(object):
    principal = attr.ib(default=None)
    secret = attr.ib(default=None)
