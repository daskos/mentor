from __future__ import absolute_import, division, print_function

import cloudpickle
from mesos.interface import mesos_pb2
from satyr.messages import PythonTask, PythonTaskStatus
from satyr.proxies.messages import TaskID, decode, encode


def test_python_task_status_decode():
    data = {'arbitrary': 'data', 'lst': [1, 2, 3]}
    dumped = cloudpickle.dumps(data)

    proto = mesos_pb2.TaskStatus(
        data=dumped,
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    status = decode(proto)

    assert isinstance(status, PythonTaskStatus)
    assert status['data'] == dumped
    assert status.data == data

    proto = mesos_pb2.TaskStatus(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    status = decode(proto)
    status.data = data

    assert isinstance(status, PythonTaskStatus)
    assert status.data == data
    assert status['data'] == dumped


def test_python_task_status_encode():
    data = {'arbitrary': 'data', 'value': 5}
    dumped = cloudpickle.dumps(data)

    status = PythonTaskStatus(task_id={'value': 'test-id'},
                              state='TASK_STAGING',
                              data=data)

    proto = encode(status)
    assert isinstance(proto, mesos_pb2.TaskStatus)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'
    assert proto.state == mesos_pb2.TASK_STAGING

    status = PythonTaskStatus(task_id={'value': 'test-id'},
                              state='TASK_RUNNING')
    status.data = data
    proto = encode(status)
    assert isinstance(proto, mesos_pb2.TaskStatus)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'
    assert proto.state == mesos_pb2.TASK_RUNNING


def test_python_task_decode():
    fn, args, kwargs = sum, [range(5)], {}
    data = (fn, args, kwargs)
    dumped = cloudpickle.dumps(data)

    proto = mesos_pb2.TaskInfo(
        data=dumped,
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    task = decode(proto)

    assert isinstance(task, PythonTask)
    assert task['data'] == dumped
    assert task.data == data

    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='python')]))
    task = decode(proto)
    task.data = data

    assert isinstance(task, PythonTask)
    assert task.data == data
    assert task['data'] == dumped


def test_python_task_encode():
    fn, args, kwargs = sum, [range(5)], {}
    data = (fn, args, kwargs)
    dumped = cloudpickle.dumps(data)

    task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                      id={'value': 'test-id'})

    proto = encode(task)
    assert isinstance(proto, mesos_pb2.TaskInfo)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'

    task = PythonTask(id=TaskID(value='test-id'))
    task.data = data
    proto = encode(task)
    assert isinstance(proto, mesos_pb2.TaskInfo)
    assert proto.data == dumped
    assert proto.task_id.value == 'test-id'


def test_python_task_execution():
    fn, args, kwargs = sum, [range(5)], {}
    task = PythonTask(fn=fn, args=args, kwargs=kwargs,
                      id={'value': 'test-id'})
    task = decode(encode(task))
    assert task() == 10

    def fn(lst1, lst2):
        return sum(lst1) - sum(lst2)
    args = [range(5), range(3)]
    task = PythonTask(fn=fn, args=args, id={'value': 'test-id'})
    task = decode(encode(task))
    assert task() == 7


# def test_python_task_callbacks(mocker):
#     fn, args, kwargs = sum, [range(5)], {}

#     on_update = mocker.MagicMock()
#     on_success = mocker.MagicMock()
#     task = PythonTask(fn=fn, args=args, kwargs=kwargs, id={'value': 'test-id'},
#                       on_update=on_update, on_success=on_success)
#     status = PythonTaskStatus(state='TASK_FINISHED', data=20)
#     task.update(status)
#     on_update.assert_called_with(task, status)
#     on_success.assert_called_with(task, status)

#     on_update = mocker.MagicMock()
#     on_fail = mocker.MagicMock()
#     task = PythonTask(fn=fn, args=args, kwargs=kwargs, id={'value': 'test-id'},
#                       on_update=on_update, on_fail=on_fail)
#     status = PythonTaskStatus(state='TASK_KILLED')
#     task.update(status)
#     on_update.assert_called_with(task, status)
#     on_fail.assert_called_with(task, status)
