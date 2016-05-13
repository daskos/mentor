from __future__ import absolute_import, division, print_function

import logging

import cloudpickle
from mesos.interface import mesos_pb2

from .proxies.messages import (CommandInfo, ContainerInfo, Cpus, Disk,
                               DockerInfo, Environment, ExecutorInfo, Mem,
                               TaskInfo, TaskStatus)


class PickleMixin(object):

    @property
    def data(self):
        return cloudpickle.loads(self['data'])

    @data.setter
    def data(self, value):
        self['data'] = cloudpickle.dumps(value)


class PythonTaskStatus(PickleMixin, TaskStatus):

    proto = mesos_pb2.TaskStatus(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))

    def __init__(self, data=None, **kwargs):
        super(PythonTaskStatus, self).__init__(**kwargs)
        self.data = data


class PythonTask(PickleMixin, TaskInfo):

    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))

    def __init__(self, fn=None, args=[], kwargs={},
                 resources=[Cpus(0.1), Mem(128), Disk(0)],
                 command='python -m satyr.executor', envs={}, uris=[],
                 docker='lensa/satyr:latest', **kwds):
        self.executor = ExecutorInfo(
            container=ContainerInfo(type='DOCKER', docker=DockerInfo(
                force_pull_image=False, network='HOST')),
            command=CommandInfo(shell=True))
        self.data = (fn, args, kwargs)
        self.envs = envs
        self.uris = uris
        self.docker = docker
        self.command = command
        self.resources = resources
        super(PythonTask, self).__init__(**kwds)

    @property
    def uris(self):
        return [uri.value for uri in self.executor.command.uris]

    @uris.setter
    def uris(self, value):
        self.executor.command.uris = [{'value': v} for v in value]

    @property
    def envs(self):
        envs = self.executor.command.environment.variables
        return {env.name: env.value for env in envs}

    @envs.setter
    def envs(self, value):
        envs = [{'name': k, 'value': v} for k, v in value.items()]
        self.executor.command.environment = Environment(variables=envs)

    @property
    def command(self):
        return self.executor.command.value

    @command.setter
    def command(self, value):
        self.executor.command.value = value

    @property
    def docker(self):
        return self.executor.container.docker.image

    @docker.setter
    def docker(self, value):
        self.executor.container.docker.image = value

    def __call__(self):
        fn, args, kwargs = self.data
        return fn(*args, **kwargs)

    def status(self, state, **kwargs):
        return PythonTaskStatus(task_id=self.task_id, state=state, **kwargs)

    def update(self, status):
        self.on_update(status)

        if status.has_succeeded():
            self.on_success(status)
        elif status.has_failed():
            self.on_fail(status)

    def on_update(self, status):
        pass

    def on_success(self, status):
        logging.info('Task {} has been succeded'.format(self.id.value))

    def on_fail(self, status):
        logging.info('Task {} has been failed due to {}'.format(self.id.value,
                                                                status.message))
