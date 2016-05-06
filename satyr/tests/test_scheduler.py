from __future__ import absolute_import, division, print_function

import pytest
from satyr.messages import PythonTask, PythonTaskStatus
from satyr.proxies.messages import (Cpus, Disk, Mem, Offer, OfferID, SlaveID,
                                    TaskID)
from satyr.scheduler import QueueScheduler, Running


@pytest.fixture
def python_task():
    task = PythonTask(id=TaskID(value='test-task-id'),
                      fn=sum, args=[range(5)],
                      resources=[Cpus(0.1), Mem(128), Disk(0)])
    return task


@pytest.fixture
def offers():
    o1 = Offer(id=OfferID(value='first-offer'),
               slave_id=SlaveID(value='test-slave'),
               resources=[Cpus(2), Mem(256), Disk(1024)])
    o2 = Offer(id=OfferID(value='second-offer'),
               slave_id=SlaveID(value='test-slave'),
               resources=[Cpus(1), Mem(1024), Disk(2048)])
    return [o1, o2]


def test_launch_decline(mocker, python_task, offers):
    driver = mocker.Mock()
    sched = QueueScheduler(name='test-scheduler')

    sched.submit(python_task)
    sched.on_offers(driver, offers)

    calls = driver.launch.call_args_list

    args, kwargs = calls[0]
    assert isinstance(args[0], OfferID)
    assert args[0].value == 'first-offer'
    assert isinstance(args[1][0], PythonTask)
    assert args[1][0].task_id.value == 'test-task-id'

    args, kwargs = calls[1]
    assert isinstance(args[0], OfferID)
    assert args[0].value == 'second-offer'
    assert args[1] == []  # declines via launch empty task list


def test_task_callbacks(mocker, python_task, offers):
    driver = mocker.Mock()
    sched = QueueScheduler(name='test-scheduler')
    mocker.spy(python_task, 'on_update')
    mocker.spy(python_task, 'on_success')

    sched.submit(python_task)
    sched.on_offers(driver, offers)

    sched.on_update(driver, python_task.status('TASK_RUNNING'))
    sched.on_update(driver, python_task.status('TASK_FINISHED',
                                               data=python_task()))

    update_calls = python_task.on_update.call_args_list
    success_calls = python_task.on_success.call_args_list

    args, kwargs = update_calls[0]
    assert isinstance(args[0], PythonTaskStatus)
    assert args[0].state == 'TASK_RUNNING'

    args, kwargs = update_calls[1]
    assert isinstance(args[0], PythonTaskStatus)
    assert args[0].state == 'TASK_FINISHED'

    args, kwargs = success_calls[0]
    assert isinstance(args[0], PythonTaskStatus)
    assert args[0].state == 'TASK_FINISHED'
    assert args[0].data == 10


def test_task_result(mocker, python_task, offers):
    driver = mocker.Mock()
    sched = QueueScheduler(name='test-scheduler')

    result = sched.submit(python_task)
    sched.on_offers(driver, offers)
    sched.on_update(driver, python_task.status('TASK_RUNNING'))
    sched.on_update(driver, python_task.status('TASK_FINISHED',
                                               data=python_task()))

    assert result.get() == 10


# integration test
def test_runner_context_manager():
    sched = QueueScheduler(name='test-scheduler')
    with Running(sched, name='test-scheduler'):
        sched.wait()

    assert sched
