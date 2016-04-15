from __future__ import absolute_import, division, print_function

from time import sleep

import pytest
from satyr.executor import BaseExecutor
from satyr.messages import PythonTask, PythonTaskStatus
from satyr.proxies.messages import CommandInfo, Cpus, Mem, TaskID, TaskInfo


class FakeThread(object):

    def __init__(self, target):
        self.target = target

    def start(self):
        return self.target()


def test_finished_status_updates(mocker):
    mocker.patch('threading.Thread', side_effect=FakeThread)

    driver = mocker.Mock()
    task = PythonTask(fn=sum, args=[range(5)])

    executor = BaseExecutor()
    executor.on_launch(driver, task)

    calls = driver.update.call_args_list

    args, kwargs = calls[0]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_RUNNING'
    assert status.result == None

    args, kwargs = calls[1]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_FINISHED'
    assert status.result == 10


def test_failed_status_updates(mocker):
    mocker.patch('threading.Thread', side_effect=FakeThread)

    def failing_function(*args):
        raise Exception("Booom!")

    driver = mocker.Mock()
    task = PythonTask(fn=failing_function, args=['arbitrary', 'args'])

    executor = BaseExecutor()
    executor.on_launch(driver, task)

    calls = driver.update.call_args_list

    args, kwargs = calls[0]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_RUNNING'
    assert status.result == None

    args, kwargs = calls[1]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_FAILED'
    assert status.result == None
    assert status.message == 'Booom!'
