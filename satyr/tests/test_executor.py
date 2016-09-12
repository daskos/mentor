from __future__ import absolute_import, division, print_function

from satyr.executor import ExecutorDriver, ThreadExecutor
from satyr.messages import PythonTask, PythonTaskStatus
from satyr.utils import RemoteException


class FakeThread(object):

    def __init__(self, target, args=(), kwargs={}):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def start(self):
        return self.target(*self.args, **self.kwargs)


def test_finished_status_updates(mocker):
    mocker.patch('threading.Thread', side_effect=FakeThread)

    driver = mocker.Mock()
    task = PythonTask(fn=sum, args=[range(5)])

    executor = ThreadExecutor()
    executor.on_launch(driver, task)

    calls = driver.update.call_args_list

    args, kwargs = calls[0]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_RUNNING'
    assert status.data is None

    args, kwargs = calls[1]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_FINISHED'
    assert status.data == 10


def test_failed_status_updates(mocker):
    mocker.patch('threading.Thread', FakeThread)

    def failing_function(*args):
        raise Exception("Booom!")

    driver = mocker.Mock()
    task = PythonTask(fn=failing_function, args=['arbitrary', 'args'])

    executor = ThreadExecutor()
    executor.on_launch(driver, task)

    calls = driver.update.call_args_list

    args, kwargs = calls[0]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_RUNNING'
    assert status.data is None

    args, kwargs = calls[1]
    status = args[0]
    assert isinstance(status, PythonTaskStatus)
    assert status.state == 'TASK_FAILED'
    assert isinstance(status.data, tuple)
    assert isinstance(status.exception, RemoteException)

    assert status.message == 'Booom!'


# def test_runner_context_manager():
#     executor = OneOffExecutor()
#     with Running(executor):
#         pass

#     assert executor
