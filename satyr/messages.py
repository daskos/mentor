from __future__ import absolute_import, division, print_function

import logging

import cloudpickle
from mesos.interface import mesos_pb2

from .proxies.messages import (CommandInfo, ContainerInfo, Cpus, Disk,
                               Environment, ExecutorInfo, Image, Mem, TaskInfo,
                               TaskStatus)
from .utils import remote_exception


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

    @property
    def exception(self):
        try:
            return remote_exception(*self.data)
        except:
            return None


# TODO create custom messages per executor
class PythonTask(PickleMixin, TaskInfo):

    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))

    def __init__(self, fn=None, args=[], kwargs={},
                 resources=[Cpus(0.1), Mem(128), Disk(0)],
                 executor=None, retries=3, **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.status = PythonTaskStatus(task_id=self.id, state='TASK_STAGING')
        self.executor = executor or PythonExecutor()
        self.data = (fn, args, kwargs)
        self.resources = resources
        self.retries = retries
        self.attempt = 1

    def __call__(self):
        fn, args, kwargs = self.data
        return fn(*args, **kwargs)

    def retry(self, status):
        if self.attempt < self.retries:
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

        try:
            raise status.exception  # won't retry due to code error in PythonTaskStatus
        except KeyError as e:
            # not a code error, e.g. problem during deployment
            self.retry(status)
        else:
            logging.error('Aborting due to task {} failed with state {} and message '
                          '{}'.format(self.id, status.state, status.message))


class PythonExecutor(ExecutorInfo):

    proto = mesos_pb2.ExecutorInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))

    def __init__(self, docker='satyr', force_pull=False,
                 envs={}, uris=[], **kwds):
        super(PythonExecutor, self).__init__(**kwds)
        self.container = ContainerInfo(
            type='MESOS',
            mesos=ContainerInfo.MesosInfo(
                image=Image(type='DOCKER',
                            docker=Image.Docker())))
        self.command = CommandInfo(value='python -m satyr.executor',
                                   shell=True)
        self.force_pull = force_pull
        self.docker = docker
        self.envs = envs
        self.uris = uris

    @property
    def docker(self):
        return self.container.mesos.image.docker.name

    @docker.setter
    def docker(self, value):
        self.container.mesos.image.docker.name = value

    @property
    def force_pull(self):
        # cached is the opposite of force pull image
        return not self.container.mesos.image.cached

    @force_pull.setter
    def force_pull(self, value):
        self.container.mesos.image.cached = not value

    @property
    def uris(self):
        return [uri.value for uri in self.command.uris]

    @uris.setter
    def uris(self, value):
        self.command.uris = [{'value': v} for v in value]

    @property
    def envs(self):
        envs = self.command.environment.variables
        return {env.name: env.value for env in envs}

    @envs.setter
    def envs(self, value):
        envs = [{'name': k, 'value': v} for k, v in value.items()]
        self.command.environment = Environment(variables=envs)
