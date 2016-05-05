from __future__ import absolute_import, division, print_function

import logging

import cloudpickle
from mesos.interface import mesos_pb2

from .proxies.messages import (CommandInfo, ContainerInfo, Cpus, Disk,
                               DockerInfo, ExecutorID, ExecutorInfo, Mem,
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


class PythonTask(PickleMixin, TaskInfo):  # TODO: maybe rename basetask

    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))

    def __init__(self, fn=None, args=[], kwargs={},
                 resources=[Cpus(0.1), Mem(64), Disk(0)], **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.resources = resources

        docker = DockerInfo(image='lensacom/satyr:latest',
                            force_pull_image=False,
                            network='HOST')

        self.executor = ExecutorInfo(
            # name='python-task-executor',
            executor_id=ExecutorID(value=self.id.value),
            command=CommandInfo(value='python -m satyr.executor', shell=True),
            container=ContainerInfo(type='DOCKER', docker=docker),
            resources=resources)

        self.data = (fn, args, kwargs)  # TODO: assert fn is callable

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
