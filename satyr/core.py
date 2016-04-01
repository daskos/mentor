from __future__ import absolute_import, division, print_function

from mesos.interface.mesos_pb2 import TaskID, Value, Environment, Volume, Resource
from mesos.interface.mesos_pb2 import TaskInfo, CommandInfo
from mesos.interface.mesos_pb2 import ContainerInfo, FrameworkInfo


def decode_typed_field(pb):
    field_type = pb.type
    if field_type == Value.SCALAR:
        return pb.scalar.value
    elif field_type == Value.RANGES:
        return [(ra.begin, ra.end) for ra in pb.ranges.range]
    elif field_type == Value.SET:
        return pb.set.item
    elif field_type == Value.TEXT:
        return pb.text.value
    else:
        raise ValueError("Unknown field type: %s", field_type)


class Framework(object):

    def __init__(self, name, user='', role='*', principal='',
                 checkpoint=False, webui_url=None):
        self.name = name
        self.user = user
        self.role = role
        self.principal = principal
        self.checkpoint = checkpoint
        self.webui_url = webui_url

    def encode(self):
        framework = FrameworkInfo(user=self.user,
                                  name=self.name,
                                  principal=self.principal,
                                  checkpoint=self.checkpoint)

        return framework


class Resources(object):

    def __init__(self, cpus, mem, disk=0, ports=[]):
        self.cpus = cpus
        self.mem = mem
        self.disk = disk
        self.ports = ports

    @classmethod
    def decode(cls, pbs):
        return cls(**{pb.name: decode_typed_field(pb) for pb in pbs})

    def encode(self):
        cpus = Resource(name='cpus', type=Value.SCALAR)
        cpus.scalar.value = self.cpus

        mem = Resource(name='mem', type=Value.SCALAR)
        mem.scalar.value = self.mem

        disk = Resource(name='disk', type=Value.SCALAR)
        disk.scalar.value = self.disk

        ranges = [Value.Range(begin=b, end=e) for b, e in self.ports]
        ports = Resource(name='ports', type=Value.RANGES)
        ports.ranges.extend(ranges)

        return [cpus, mem, disk, ports]

    def __cmp__(self, other):
        this = (self.cpus, self.mem, self.disk)
        other = (other.cpus, other.mem, other.disk)
        if this < other:
            return -1
        elif this > other:
            return 1
        else:
            return 0

    def __add__(self, other):
        ports = list(set(self.ports) | set(other.ports))
        disk = self.disk + other.disk
        cpus = self.cpus + other.cpus
        mem = self.mem + other.mem
        return Resources(cpus=cpus, mem=mem, disk=disk, ports=ports)

    def __sub__(self, other):
        ports = list(set(self.ports) - set(other.ports))
        disk = self.disk - other.disk
        cpus = self.cpus - other.cpus
        mem = self.mem - other.mem
        return Resources(cpus=cpus, mem=mem, disk=disk, ports=ports)


class Offer(object):  # read-only offer wrapper created from OfferInfo

    def __init__(self, pb):
        self.pb = pb

    @classmethod
    def decode(cls, pb):
        return cls(pb=pb)

    def encode(self):
        return self.pb

    def __getattr__(self, name):
        return getattr(self.pb, name)

    def __hash__(self):
        return hash(self.pb.id.value)

    @property
    def resources(self):
        return Resources.decode(self.pb.resources)


class Docker(object):

    def __init__(self, image, force_pull=False, volumes=[], network='HOST'):
        self.image = image
        self.force_pull = force_pull
        self.volumes = volumes
        self.network = network

    def encode(self):
        volumes = [Volume(host_path=host,
                          container_path=container,
                          mode=Volume.Mode.Value(mode.upper()))
                   for host, container, mode in self.volumes]

        docker = ContainerInfo.DockerInfo(image=self.image,
                                          force_pull_image=self.force_pull,
                                          network=DockerInfo.Network.Value(
                                              self.network.upper()))

        container = ContainerInfo(type=ContainerInfo.DOCKER,
                                  volumes=volumes,
                                  docker=docker)

        return container


class Task(object):  # created manually, converted to TaskInfo

    def __init__(self, tid, name, resources, container=None):
        self.tid = tid
        self.name = name
        self.resources = resources
        self.container = container

    def encode(self, offer):
        task = TaskInfo(name=self.name,
                        task_id=TaskID(value=self.tid),
                        slave_id=offer.slave_id,
                        resources=self.resources.encode())
        if self.container:
            task.container.MergeFrom(self.container.encode())

        return task

    def __cmp__(self, other):
        return self.resources.__cmp__(other.resources)


class Command(Task):

    # additional arguments: shell, user
    def __init__(self, tid, name, cmd, resources, args=[], envs={}, uris=[],
                 container=None):
        super(Command, self).__init__(tid=tid, name=name, resources=resources,
                                      container=container)
        self.cmd = cmd
        self.args = args
        self.envs = envs
        self.uris = uris

    def encode(self):
        uris = [CommandInfo.URI(value=uri) for uri in self.uris]
        envs = [Environment.Variable(name=k, value=v)
                for k, v in self.envs.items()]

        command = CommandInfo(value=self.cmd,
                              arguments=self.args,
                              environment=envs,
                              uris=uris)

        task = super(Command, self).encode()
        task.command.MergeFrom(command)

        return task


class Python(Task):

    def __init__(self, tid, name, fn, resources, args=[], envs={}, uris=[],
                 container=None):

        super(Python, self).__init__(tid=tid, name=name, resources=resources,
                                     container=container)
        self.fn = fn
        self.args = args
        self.envs = envs
        self.uris = uris

    def encode(self):  # TODO
        pass
