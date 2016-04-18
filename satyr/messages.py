from __future__ import absolute_import, division, print_function

from uuid import uuid4

import cloudpickle
from mesos.interface import mesos_pb2

from .proxies.messages import (Cpus, Disk, Mem, ResourcesMixin, TaskInfo,
                               TaskStatus, decode, encode)


class PythonTaskStatus(TaskStatus):

    proto = mesos_pb2.TaskStatus(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))

    def __init__(self, result=None, **kwargs):
        super(PythonTaskStatus, self).__init__(**kwargs)
        self.result = result

    @property
    def result(self):
        return cloudpickle.loads(self['data'])

    @result.setter
    def result(self, value):
        self['data'] = cloudpickle.dumps(value)


class PythonTask(TaskInfo):

    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))

    def __init__(self, fn=None, args=[], kwargs={},
                 resources=[Cpus(1), Mem(64), Disk(0)], **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.resources = resources
        self.executor.name = 'test-executor'
        self.executor.executor_id.value = self.task_id.value
        self.executor.resources = resources
        self.executor.command.value = 'python -m satyr.executor'
        self.executor.command.shell = True
        self.executor.container.type = 'DOCKER'
        self.executor.container.docker.image = 'lensacom/satyr:latest'
        self.executor.container.docker.network = 'HOST'
        self.executor.container.docker.force_pull_image = False

        self.callback = (fn, args, kwargs)

    def __call__(self):
        fn, args, kwargs = self.callback
        return fn(*args, **kwargs)

    def status(self, state, message='', result=None):
        return PythonTaskStatus(task_id=self.task_id,
                                state=state,
                                message=message,
                                result=result)

    @property
    def callback(self):
        return cloudpickle.loads(self['data'])

    @callback.setter
    def callback(self, value):
        self['data'] = cloudpickle.dumps(value)
