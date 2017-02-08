from __future__ import absolute_import, division, print_function

import cloudpickle

from mentor.messages import TaskInfo,Message
from mentor.messages import PythonTask, PythonTaskStatus,PythonExecutor
from mentor.utils import RemoteException


# TODO Not working for some reason?
def test_python_task_status_decode():
    data = {'arbitrary': 'data', 'lst': [1, 2, 3]}
    dumped = cloudpickle.dumps(data)

    proto = PythonTaskStatus(
        data=dumped,
        labels=[{"key": "python"}])

    status = proto

    assert isinstance(status, Message)
    assert status['data'] == dumped
    assert status.cdata == data

    proto = Message(
        data=dumped,
        labels=[{"key": "python"}])

    status = proto
    status.cdata = data
    # TODO Not working for some reason?
    assert isinstance(status, Message)
    assert status.cdata == data
    assert status['data'] == dumped


def test_python_task_status_encode():
    data = {'arbitrary': 'data', 'value': 5}
    dumped = cloudpickle.dumps(data)

    status = PythonTaskStatus(task_id=Message(value='test-id'), state='TASK_STAGING',
                              data=data)
    proto = status
    assert isinstance(proto, PythonTaskStatus)
    assert proto.data == data
    assert proto.task_id.value == 'test-id'
    assert proto.state == "TASK_STAGING"

    status = PythonTaskStatus(task_id='test-id', state='TASK_RUNNING')
    status.data = data
    proto = status
    assert isinstance(proto, PythonTaskStatus)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'
    assert proto.state == "TASK_RUNNING"


def test_python_task_decode():
    fn, args, kwargs = sum, [range(5)], {}
    data = (fn, args, kwargs)
    dumped = cloudpickle.dumps(data)

    proto = TaskInfo(
        labels=[{"key": "python"}])
    task = proto

    assert isinstance(task, PythonTask)
    assert task['data'] == dumped
    assert task.data == data

    proto = TaskInfo(
        labels=[{"key": "python"}])
    task = proto
    task.data = data

    assert isinstance(task, PythonTask)
    assert task.data == data
    assert task['data'] == dumped


def test_python_task_encode():
    fn, args, kwargs = sum, [range(5)], {}
    data = (fn, args, kwargs)
    dumped = cloudpickle.dumps(data)

    task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                      task_id='test-id',
                      envs={'TEST': 'value'},
                      uris=['test_dependency'])

    proto = task
    assert isinstance(proto, TaskInfo)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'
    assert proto.executor.command.uris[0].value == 'test_dependency'
    assert proto.executor.command.environment.variables[0].name == 'TEST'
    assert proto.executor.command.environment.variables[0].value == 'value'

    task = PythonTask(id=Message(value='test-id'))
    task.data = data
    proto = task
    assert isinstance(proto, TaskInfo)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'


def test_python_task_execution():
    fn, args, kwargs = sum, [range(5)], {}
    task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                      id='test-id')
    assert task() == 10

    def fn(lst1, lst2):
        return sum(lst1) - sum(lst2)
    args = [range(5), range(3)]
    task = PythonTask(fn=fn, args=args, id='test-id')
    task = task
    assert task() == 7


def test_python_task_contains_status():
    fn, args, kwargs = sum, [range(5)], {}

    task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                      id='test-id',
                      envs={'TEST': 'value'},
                      uris=['test_dependency'])

    assert isinstance(task.status, PythonTaskStatus)
    assert task.status.state == 'TASK_STAGING'

    new_status = PythonTaskStatus(task_id=task.id, state='TASK_RUNNING')
    task.update(new_status)

    assert isinstance(task.status, PythonTaskStatus)
    assert task.status.state == 'TASK_RUNNING'


def test_python_task_status_exception():
    status = PythonTaskStatus(task_id=Message(value='e'),
                              state='TASK_FAILED')
    status.data = (TypeError('test'), 'traceback')

    assert isinstance(status.exception, RemoteException)
    assert isinstance(status.exception, TypeError)
