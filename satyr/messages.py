from __future__ import absolute_import, division, print_function

from uuid import uuid4

import cloudpickle
from mesos.interface import mesos_pb2

from .proxies.messages import (Cpus, Disk, Mem, TaskInfo, TaskStatus, decode,
                               encode)


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
        self.executor.executor_id.value = str(uuid4())
        self.executor.command.value = 'python -m satyr.executor'
        self.container.type = 'DOCKER'
        self.container.docker.image = 'lensacom/satyr:latest'
        self.callback = (fn, args, kwargs)

    def __call__(self):
        fn, args, kwargs = self.callback
        return fn(*args, **kwargs)

    def status(self, state, message='', result=None):
        return PythonTaskStatus(task_id=self.id,
                                state=state,
                                message=message,
                                result=result)

    @property
    def callback(self):
        return cloudpickle.loads(self['data'])

    @callback.setter
    def callback(self, value):
        self['data'] = cloudpickle.dumps(value)
