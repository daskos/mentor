import cloudpickle
import pytest
from mesos.interface import mesos_pb2
from satyr.messages import PythonTask, PythonTaskStatus, decode, encode


def test_python_task_status_decode():
    result = {'arbitrary': 'data', 'lst': [1, 2, 3]}
    dumped = cloudpickle.dumps(result)

    proto = mesos_pb2.TaskStatus(
        data=dumped,
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    status = decode(proto)

    assert isinstance(status, PythonTaskStatus)
    assert status['data'] == dumped
    assert status.result == result

    proto = mesos_pb2.TaskStatus(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    status = decode(proto)
    status.result = result

    assert isinstance(status, PythonTaskStatus)
    assert status.result == result
    assert status['data'] == dumped


def test_python_task_status_encode():
    result = {'arbitrary': 'data', 'value': 5}
    dumped = cloudpickle.dumps(result)

    status = PythonTaskStatus(task_id={'value': 'test-id'},
                              state='TASK_STAGING',
                              result=result)

    proto = encode(status)
    assert isinstance(proto, mesos_pb2.TaskStatus)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'
    assert proto.state == mesos_pb2.TASK_STAGING

    status = PythonTaskStatus(task_id={'value': 'test-id'},
                              state='TASK_RUNNING')
    status.result = result
    proto = encode(status)
    assert isinstance(proto, mesos_pb2.TaskStatus)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'
    assert proto.state == mesos_pb2.TASK_RUNNING


def test_python_task_decode():
    fn, args, kwargs = sum, [range(5)], {}
    callback = (fn, args, kwargs)
    dumped = cloudpickle.dumps(callback)

    proto = mesos_pb2.TaskInfo(
        data=dumped,
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    task = decode(proto)

    assert isinstance(task, PythonTask)
    assert task['data'] == dumped
    assert task.callback == callback

    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    task = decode(proto)
    task.callback = callback

    assert isinstance(task, PythonTask)
    assert task.callback == callback
    assert task['data'] == dumped


def test_python_task_encode():
    fn, args, kwargs = sum, [range(5)], {}
    callback = (fn, args, kwargs)
    dumped = cloudpickle.dumps(callback)

    task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                      task_id={'value': 'test-id'})

    proto = encode(task)
    assert isinstance(proto, mesos_pb2.TaskInfo)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'

    task = PythonTask(task_id={'value': 'test-id'})
    task.callback = callback
    proto = encode(task)
    assert isinstance(proto, mesos_pb2.TaskInfo)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'


def test_python_task_execution():
    fn, args, kwargs = sum, [range(5)], {}
    task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                      task_id={'value': 'test-id'})
    task = decode(encode(task))
    assert task() == 10

    def fn(lst1, lst2):
        return sum(lst1) - sum(lst2)
    args = [range(5), range(3)]
    task = PythonTask(fn=fn, args=args, task_id={'value': 'test-id'})
    task = decode(encode(task))
    assert task() == 7
