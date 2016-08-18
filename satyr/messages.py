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
                 docker='lensa/satyr:latest', force_pull=False, retries=3,
                 **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.status = PythonTaskStatus(task_id=self.id, state='TASK_STAGING')
        self.executor = ExecutorInfo(
            container=ContainerInfo(type='DOCKER',
                                    docker=DockerInfo(network='HOST')),
            command=CommandInfo(shell=True))
        self.data = (fn, args, kwargs)
        self.envs = envs
        self.uris = uris
        self.docker = docker
        self.force_pull = force_pull
        self.command = command
        self.resources = resources
        self.retries = retries
        self.attempt = 1

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

    @property
    def force_pull(self):
        return self.executor.container.docker.force_pull_image

    @force_pull.setter
    def force_pull(self, value):
        self.executor.container.docker.force_pull_image = value

    def __call__(self):
        fn, args, kwargs = self.data
        return fn(*args, **kwargs)

    def update(self, status):
        assert isinstance(status, TaskStatus)
        self.on_update(status)
        if status.has_succeeded():
            self.on_success(status)
        elif status.has_failed():
            self.on_fail(status)

    def on_update(self, status):
        self.status = status  # update task's status
        logging.info('Task {} has been updated with state {}'.format(
            self.id.value, status.state))

    def on_success(self, status):
        logging.info('Task {} has been succeded'.format(self.id.value))

    def on_fail(self, status):
        logging.error('Task {} has been failed with state {} due to {}'.format(
            self.id.value, status.state, status.message))

        if isinstance(status.data, Exception):  # won't retry due to code error
            logging.error('Aborting due to task {} failed with state {} and message '
                          '{}'.format(self.id, status.state, status.message))
            raise status.data
        elif self.attempt < self.retries:
            logging.info('Task {} attempt #{} rescheduled due to failure with state '
                         '{} and message {}'.format(self.id, self.attempt,
                                                    status.state, status.message))
            self.attempt += 1
            status.state = 'TASK_STAGING'
        else:
            logging.error('Aborting due to task {} failed for {} attempts in state '
                          '{} with message {}'.format(self.id, self.retries,
                                                      status.state, status.message))
            raise RuntimeError('Task {} failed with state {} and message {}'.format(
                self.id, status.state, status.message))
