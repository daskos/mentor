from __future__ import absolute_import, division, print_function

import logging

import cloudpickle
import attr
from mentor.messages.baseold import (  Cpus, Disk,
                                    Mem, Label,
                                    Image)
from mentor.utils import remote_exception

from mentos.utils import encode_data, decode_data

log = logging.getLogger(__name__)



class PickleMixin(object):

    @property
    def cdata(self):
        return cloudpickle.loads(self.data)

    @cdata.setter
    def cdata(self, value):
        self.data = cloudpickle.dumps(value)


@attr.s
class PythonExecutor(object):


    labels = [Label(key='python',value="")]
    docker = attr.ib(default="mentor")
    force_pull = attr.ib(default=False)
    envs = attr.ib(default={})
    uris = attr.ib(default=[])

    # container = ContainerInfo(
    #     type='MESOS',
    #     mesos=ContainerInfo.MesosInfo(
    #         image=Image(type='DOCKER',
    #                     docker=ContainerInfo.DockerInfo())))
    # command = CommandInfo(value='python -m mentor.executor',
    #                            shell=True)

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

    # @envs.setter
    # def envs(self, value):
    #     envs = [{'name': k, 'value': v} for k, v in value.items()]
    #     self.command.environment = Environment(variables=envs)
    #

@attr.s
class PythonTaskStatus(PickleMixin):

    labels = [Label(key='python',value="")]

    @property
    def exception(self):
        try:
            return remote_exception(*self.data)
        except:
            return None


# TODO create custom messages per executor
@attr.s
class PythonTask(PickleMixin, object):

    labels = [Label(key='python',value="")]
    fn = attr.ib(default=None)

    resources =[Cpus(0.1), Mem(128), Disk(0)]
    retries = 3
    attempt = 1
    args = attr.ib(default=None)
    kwargs = attr.ib(default=None)
    envs = attr.ib(default=None)
    uris = attr.ib(default=None)
    id = attr.ib(default=None)
    #task_id  = TaskID(value=id)
    #executor = attr.ib(default=PythonExecutor())

    @property
    def docker(self):
        return self.container.mesos.image.docker.name

    @docker.setter
    def docker(self, value):
        self.container.mesos.image.docker.name = value
    def __attrs_post_init__(self):
        pass
        #self.status = PythonTaskStatus(task_id=TaskID(value=self.task_id), state='TASK_STAGING')
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
       # assert isinstance(status, TaskStatus)
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
