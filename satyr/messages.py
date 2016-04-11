from __future__ import absolute_import, division, print_function

from uuid import uuid4

import cloudpickle
from mesos.interface import mesos_pb2

from .proxies.messages import Cpus, Disk, Mem, TaskInfo


class PythonTask(TaskInfo):
    # proto = mesos_pb2.TaskInfo(labels=mesos_pb2.Labels(
    #    labels=[mesos_pb2.Label(key='python')])
    proto = mesos_pb2.TaskInfo(name='python-task')

    def __init__(self, tid=None, fn=None, args=[], kwargs={},
                 resources=[Cpus(0), Mem(64), Disk(0)], **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.task_id.value = tid
        self.resources = resources

        self.executor.executor_id.value = str(uuid4())
        self.executor.command.value = 'python -m satyr.executor'
        self.executor.container.type = 'MESOS'

        self.data = cloudpickle.dumps((fn, args, kwds))
        #self.command = CommandInfo(value='echo 100')

    def __call__(self):
        fn, args, kwds = cloudpickle.loads(self.data)
        return fn(*args, **kwds)
