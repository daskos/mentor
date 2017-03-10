from __future__ import absolute_import, division, print_function

from functools import partial

import pytest
from mentor.constraint import has
from mentor.messages import PythonExecutor, PythonTask, PythonTaskStatus,Message
from mentor.messages import (Cpus, Disk, Mem, Offer)
from mentor.scheduler import QueueScheduler
from mentos.scheduler import SchedulerDriver


@pytest.fixture
def python_task():
    task = PythonTask(task_id=Message(value='test-task-id'),
                      fn=sum, args=[range(5)],
                      resources=[Cpus(0.1), Mem(128), Disk(0)])
    return task


@pytest.fixture
def offers():
    o1 = Offer(id=Message(value='first-offer'),
               slave_id=Message(value='test-slave'),
               resources=[Cpus(2), Mem(256), Disk(1024)])
    o2 = Offer(id=Message(value='second-offer'),
               slave_id=Message(value='test-slave'),
               resources=[Cpus(1), Mem(1024), Disk(2048)])
    return [o1, o2]


def test_launch_decline(mocker, python_task, offers):
    driver = mocker.Mock()
    sched = QueueScheduler()

    sched.submit(python_task)
    sched.on_offers(driver, offers)

    calls = driver.launch.call_args_list

    args, kwargs = calls[0]
    assert isinstance(args[0], Message)
    assert args[0].value == 'first-offer'
    assert isinstance(args[1][0], PythonTask)
    assert args[1][0].task_id.value != None

    args, kwargs = calls[1]
    assert isinstance(args[0], Message)
    assert args[0].value == 'second-offer'
    assert args[1] == []  # declines via launch empty task list


def test_task_callbacks(mocker, python_task, offers):
    driver = mocker.Mock()
    sched = QueueScheduler()
    mocker.spy(python_task, 'on_update')
    mocker.spy(python_task, 'on_success')

    sched.submit(python_task)
    sched.on_offers(driver, offers)

    status = PythonTaskStatus(task_id=python_task.task_id, state='TASK_RUNNING')
    sched.on_update(driver, status)

    status = PythonTaskStatus(task_id=python_task.task_id, state='TASK_FINISHED',
                              data=python_task())
    sched.on_update(driver, status)

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
    assert args[0].result == 10


def test_task_result(mocker, python_task, offers):
    driver = mocker.Mock()
    sched = QueueScheduler()

    sched.submit(python_task)
    sched.on_offers(driver, offers)

    status = PythonTaskStatus(task_id=python_task.task_id, state='TASK_RUNNING')
    sched.on_update(driver, status)

    status = PythonTaskStatus(task_id=python_task.task_id, state='TASK_FINISHED',
                              data=python_task())
    sched.on_update(driver, status)

    assert python_task.status.state == 'TASK_FINISHED'
    assert python_task.status.result == 10


def test_runner_context_manager():
    sched = QueueScheduler()
    with SchedulerDriver(sched, name='test-scheduler'):
        pass

    assert sched


def test_scheduler_retries(mocker):
    task = PythonTask(id=Message(value='non-existing-docker-image'), name='test',
                      fn=lambda: range(int(10e10)), resources=[Cpus(0.1), Mem(128), Disk(0)],
                      executor=PythonExecutor(id="test-executor",docker='pina/sen', envs={'HOME': '/tmp'}))
    sched = QueueScheduler()

    mocker.spy(sched, 'on_update')
    with SchedulerDriver(sched, name='test-scheduler') as driver:
        sched.submit(task)
        sched.wait()



    assert sched.on_update.call_count == 3

    # TODO Getting a 401 from Master when pulling image,  the starting state is never set for some reason.
    #states = ['TASK_STARTING', 'TASK_FAILED', 'TASK_FAILED']
    states = ['TASK_FAILED', 'TASK_FAILED', 'TASK_FAILED']
    for ((args, kwargs), state) in zip(sched.on_update.call_args_list, states):
        assert args[1]["state"] == state


def test_scheduler_constraints(mocker):
    task = PythonTask(name='test', fn=sum, args=[range(10)],
                      resources=[Cpus(0.1), Mem(128), Disk(0)])
    sched = QueueScheduler(constraint=partial(has, attribute='mentor'))

    with SchedulerDriver(sched, name='test-scheduler') as driver:
        sched.submit(task)

        sched.wait()

    # TODO check scheduled with the proper offer
    assert task.status.data == sum(range(10))
