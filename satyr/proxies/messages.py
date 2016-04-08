from __future__ import absolute_import, division, print_function

from google.protobuf.message import Message
from mesos.interface import mesos_pb2

from . import protobuf



# def auto(message):
#     def decode(self):
#         return dict_to_protobuf(mapping.__class__, self)
#     clsname = message.__class__.__name__
#     typ = type(clsname, (Map,), {'decode': decode})
#     return typ(protobuf_to_dict(message))


# black magic
# TODO MessageProxy
# write

class RegisterProxies(type):

    def __init__(cls, name, bases, nmspc):
        super(RegisterProxies, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = []
        cls.registry.append((cls.proto, cls))
        #cls.registry -= set(bases) # Remove base classes

    # Metamethods, called on class objects:
    def __iter__(cls):
        return iter(cls.registry)

    def __str__(cls):
        if cls in cls.registry:
            return cls.__name__
        return cls.__name__ + ": " + ", ".join([sc.__name__ for sc in cls])


class Map(dict):

    def __init__(self, mapping=None, **kwargs):
        mapping = mapping or kwargs
        for k, v in mapping.items():
            if isinstance(v, dict):
                mapping[k] = Map(v)
            elif hasattr(v, '__iter__'):
                mapping[k] = map(Map, v)
        super(Map, self).__init__(mapping)
        self.__dict__ = self

    def __hash__(self):
        return hash(frozenset(self))


class MessageProxy(Map):

    __metaclass__ = RegisterProxies

    proto = Message

    def __init__(self, message=None, **kwargs):
        mapping = protobuf.decode(message)
        return super(MessageProxy, self).__init__(mapping, **kwargs)

    def encode(self):
        return protobuf.encode(self, self.proto, MessageProxy)


# use these message proxies in scheduler and executor abstracionts
class Offer(MessageProxy):
    proto = mesos_pb2.Offer

    @property
    def id(self):
        return OfferID(self.id)

class MasterInfo(MessageProxy):
    proto = mesos_pb2.MasterInfo

class FrameworkInfo(MessageProxy):
    proto = mesos_pb2.FrameworkInfo

class ExecutorInfo(MessageProxy):
    proto = mesos_pb2.ExecutorInfo

class SlaveInfo(MessageProxy):
    proto = mesos_pb2.SlaveInfo

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

class TaskStatus(MessageProxy):
    proto = mesos_pb2.TaskStatus

class TaskInfo(MessageProxy):
    proto = mesos_pb2.TaskInfo


# class Offer(Map):


#     def __cmp__(self, other):
#         # extract resources stb.
#         pass


# class Resources(object):

#     def __init__(self, cpus, mem, disk=0, ports=[]):
#         self.cpus = cpus
#         self.mem = mem
#         self.disk = disk
#         self.ports = ports

#     @classmethod
#     def decode(cls, pbs):
#         return cls(**{pb.name: decode_typed_field(pb) for pb in pbs})

#     def encode(self):
#         cpus = mesos_pb2.Resource(name='cpus', type=mesos_pb2.Value.SCALAR)
#         cpus.scalar.value = self.cpus

#         mem = mesos_pb2.Resource(name='mem', type=mesos_pb2.Value.SCALAR)
#         mem.scalar.value = self.mem

#         disk = mesos_pb2.Resource(name='disk', type=mesos_pb2.Value.SCALAR)
#         disk.scalar.value = self.disk

#         #ranges = [mesos_pb2.Value.Range(begin=b, end=e) for b, e in self.ports]
#         #ports = mesos_pb2.Resource(name='ports', type=mesos_pb2.Value.RANGES)
#         #ports.ranges.extend(ranges)

#         return [cpus, mem, disk]

#     def __cmp__(self, other):
#         this = (self.cpus, self.mem, self.disk)
#         other = (other.cpus, other.mem, other.disk)
#         if this < other:
#             return -1
#         elif this > other:
#             return 1
#         else:
#             return 0

#     def __add__(self, other):
#         ports = list(set(self.ports) | set(other.ports))
#         disk = self.disk + other.disk
#         cpus = self.cpus + other.cpus
#         mem = self.mem + other.mem
#         return Resources(cpus=cpus, mem=mem, disk=disk, ports=ports)

#     def __sub__(self, other):
#         ports = list(set(self.ports) - set(other.ports))
#         disk = self.disk - other.disk
#         cpus = self.cpus - other.cpus
#         mem = self.mem - other.mem
#         return Resources(cpus=cpus, mem=mem, disk=disk, ports=ports)


# class Offer(object):  # read-only offer wrapper created from OfferInfo

#     def __init__(self, pb):
#         self.pb = pb

#     @classmethod
#     def decode(cls, pb):
#         return cls(pb=pb)

#     def encode(self):
#         return self.pb

#     def __getattr__(self, name):
#         return getattr(self.pb, name)

#     def __hash__(self):
#         return hash(self.pb.id.value)

#     # @property
#     # def resources(self):
#     #     return Resources.decode(self.pb.resources)

#     # def reserve(self, resources):
#     #     pass

#     # def unreserve(self, resources):
#     #     pass

#     # def launch(self, tasks):
#     #     task_infos = [task.encode(self.pb) for task in tasks]
#     #     return self.driver.launchTaks(self.id, task_infos, filters=None)  # filters?

#     # def decline(self):
#     #     return self.driver.declineOffer(self.pb.id)


# class Docker(object):

#     def __init__(self, image, force_pull=False, volumes=[], network='HOST'):
#         self.image = image
#         self.force_pull = force_pull
#         self.volumes = volumes
#         self.network = network

#     def encode(self):
#         volumes = [mesos_pb2.Volume(host_path=host,
#                                     container_path=container,
#                                     mode=Volume.Mode.Value(mode.upper()))
#                    for host, container, mode in self.volumes]

#         docker = mesos_pb2.ContainerInfo.DockerInfo(
#             image=self.image,
#             force_pull_image=self.force_pull,
#             network=mesos_pb2.DockerInfo.Network.Value(self.network.upper()))

#         container = mesos_pb2.ContainerInfo(type=mesos_pb2.ContainerInfo.DOCKER,
#                                             volumes=volumes,
#                                             docker=docker)

#         return container


# # SchedulerTask
# class Task(object):  # created manually, converted to TaskInfo

#     def __init__(self, tid, name, resources, container=None):
#         self.tid = tid
#         self.name = name
#         self.resources = resources
#         self.container = container

#     @classmethod
#     def decode(cls, pb):
#         return cls(**pb)

#     def encode(self, offer):
#         task = mesos_pb2.TaskInfo(name=self.name,
#                                   task_id=mesos_pb2.TaskID(value=self.tid),
#                                   slave_id=offer.slave_id,
#                                   resources=self.resources.encode())
#         if self.container:
#             task.container.MergeFrom(self.container.encode())

#         return task

#     def __cmp__(self, other):
#         return self.resources.__cmp__(other.resources)

#     # executor side actions
#     def run(self, driver):
#         status = TaskStatus(tid=self.tid, state=mesos_pb2.TASK_RUNNING)
#         driver.update(status)

#     def fail(self, driver):
#         status = TaskStatus(tid=self.tid, state=mesos_pb2.TASK_FAILED)
#         driver.update(status)

#     def finish(self, driver):
#         status = TaskStatus(tid=self.tid, state=mesos_pb2.TASK_FINISHED)
#         driver.update(status)

#     # scheduler side events
#     # def on_starting(scheduler, driver):
#     #     pass

#     # def on_lost(scheduler, driver):
#     #     pass

#     # def on_failed(scheduler, driver):
#     #     pass

#     # def on_finished(scheduler, driver):
#     #     pass


# class TaskStatus(object):

#     def __init__(self, tid, state, message=None, data=None):
#         self.tid = tid
#         self.state = state
#         self.message = message
#         self.data = data

#     @classmethod
#     def decode(cls, pb):
#         return cls(**pb)

#     def encode(self):
#         status = mesos_pb2.TaskStatus(task_id=mesos_pb2.TaskID(value=self.tid),
#                                       state=self.state,
#                                       message=self.message,
#                                       data=self.data)
#         return status


# class Command(Task):

#     # additional arguments: shell, user
#     def __init__(self, tid, name, cmd, resources, args=[], envs={}, uris=[],
#                  container=None):
#         super(Command, self).__init__(tid=tid, name=name, resources=resources,
#                                       container=container)
#         self.cmd = cmd
#         self.args = args
#         self.envs = envs
#         self.uris = uris

#     def encode(self):
#         uris = [mesos_pb2.CommandInfo.URI(value=uri) for uri in self.uris]
#         envs = [mesos_pb2.Environment.Variable(name=k, value=v)
#                 for k, v in self.envs.items()]

#         command = mesos_pb2.CommandInfo(value=self.cmd,
#                                         arguments=self.args,
#                                         environment=envs,
#                                         uris=uris)

#         task = super(Command, self).encode()
#         task.command.MergeFrom(command)

#         return task


# class Python(Task):

#     def __init__(self, tid, name, fn, resources, args=[], envs={}, uris=[],
#                  container=None):

#         super(Python, self).__init__(tid=tid, name=name, resources=resources,
#                                      container=container)
#         self.fn = fn
#         self.args = args
#         self.envs = envs
#         self.uris = uris

#     def encode(self):  # TODO
#         pass
