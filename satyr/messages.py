from __future__ import absolute_import, division, print_function

import logging

import cloudpickle

from satyr.proxies.messages import (CommandInfo, ContainerInfo, Cpus, Disk,
                                 Environment, ExecutorInfo, Mem, DockerInfo,
                                 TaskInfo, TaskStatus, Image)
from satyr.utils import remote_exception

from malefico.utils import encode_data, decode_data

log = logging.getLogger(__name__)


class PickleMixin(object):

    @property
    def data(self):
        return cloudpickle.loads(decode_data(self['data']))

    @data.setter
    def data(self, value):
        self['data'] = encode_data(cloudpickle.dumps(value))


class PythonTaskStatus(PickleMixin, TaskStatus):

    def __init__(self, data=None, **kwargs):
        super(PythonTaskStatus, self).__init__(**kwargs)
        self.labels = {"labels": [{"key": "python"}]}
        self.data = data

    @property
    def exception(self):
        try:
            return remote_exception(*self.data)
        except:
            return None


# TODO create custom messages per executor
class PythonTask(PickleMixin, TaskInfo):

    def __init__(self, fn=None, args=[], kwargs={},
                 resources=[Cpus(0.1), Mem(128), Disk(0)],
                 executor=None, retries=3, name="python-task", **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.status = PythonTaskStatus(
            task_id=self.task_id, state='TASK_STAGING')
        self.executor = executor or PythonExecutor()
        if "data" not in kwargs:
            self.data = (fn, args, kwargs)
        self.resources = resources
        self.name = name
        self.retries = retries
        self.attempt = 1
        self.labels = {"labels": [{"key": "python"}]}

    def __call__(self):

        fn, args, kwargs = self.data
        return fn(*args, **kwargs)

    def retry(self, status):
        if self.attempt < self.retries:
            log.info('Task {} attempt #{} rescheduled due to failure with state '
                     '{} and message {}'.format(self.task_id, self.attempt,
                                                status.state, status.message))
            self.attempt += 1
            status.state = 'TASK_STAGING'
        else:
            log.error('Aborting due to task {} failed for {} attempts in state '
                      '{} with message {}'.format(self.task_id, self.retries,
                                                  status.state, status.message))
            raise RuntimeError('Task {} failed with state {} and message {}'.format(
                self.task_id, status.state, status.message))

    def update(self, status):
        assert isinstance(status, TaskStatus)
        self.on_update(status)
        if status.has_succeeded():
            self.on_success(status)
        elif status.has_failed():
            self.on_fail(status)

    def on_update(self, status):
        self.status = status  # update task's status
        log.info('Task {} has been updated with state {}'.format(
            self.task_id.value, status.state))

    def on_success(self, status):
        log.info('Task {} has been succeded'.format(self.task_id.value))

    def on_fail(self, status):
        log.error('Task {} has been failed with state {} due to {}'.format(
            self.task_id.value, status.state, status.message))

        try:
            raise status.exception  # won't retry due to code error in PythonTaskStatus
        except KeyError as e:
            # not a code error, e.g. problem during deployment
            self.retry(status)
        else:
            log.error('Aborting due to task {} failed with state {} and message '
                      '{}'.format(self.task_id, status.state, status.message))


class PythonExecutor(ExecutorInfo):

    def __init__(self, docker='satyr', force_pull=False,
                 envs={}, uris=[], **kwds):
        super(PythonExecutor, self).__init__(**kwds)
        # self.container = ContainerInfo(
        #     type='MESOS',
        #     mesos=ContainerInfo.MesosInfo(
        #         image=Image(type='DOCKER',
        #                     docker=Image.Docker())))
        self.container = ContainerInfo(type='DOCKER',
                                       docker=DockerInfo(network='HOST'))
        self.command = CommandInfo(value='python -m satyr.executor',
                                   shell=True)
        self.docker = docker
        self.force_pull = force_pull

        self.envs = envs
        self.uris = uris
        self.labels = {"labels": [{"key": "python"}]}

    # @property
    # def docker(self):
    #     return self.container.mesos.image.docker.name
    #
    # @docker.setter
    # def docker(self, value):
    #     self.container.mesos.image.docker.name = value

    @property
    def docker(self):
        return self.container.docker.image

    @docker.setter
    def docker(self, value):
        self.container.docker.image = value

    # @property
    # def force_pull(self):
    #     # cached is the opposite of force pull image
    #     return not self.container.mesos.image.cached
    #
    # @force_pull.setter
    # def force_pull(self, value):
    #     self.container.docker.image.cached = not value

    @property
    def force_pull(self):
        return self.container.docker.force_pull_image

    @force_pull.setter
    def force_pull(self, value):
        self.container.docker.force_pull_image = value

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
