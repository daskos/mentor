from __future__ import absolute_import, division, print_function

import pytest
from satyr.messages import PythonTask
from satyr.proxies.messages import (CommandInfo, Cpus, Disk, Mem, Offer,
                                    OfferID, SlaveID, TaskID, TaskInfo)
from satyr.scheduler import BaseScheduler


@pytest.fixture
def python_task():
    task = PythonTask(task_id=TaskID(value='test-task-id'),
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
    sched = BaseScheduler(name='test-scheduler')

    sched.submit(python_task)
    sched.on_offers(driver, offers)

    calls = driver.launch.call_args_list

    args, kwargs = calls[0]
    assert isinstance(args[0], OfferID)
    assert args[0].value == 'first-offer'
    assert isinstance(args[1][0], PythonTask)
    assert args[1][0].task_id.value == 'test-task-id'

    calls = driver.decline.call_args_list
    args, kwargs = calls[0]
    assert isinstance(args[0], OfferID)
    assert args[0].value == 'second-offer'


def test_status_update(mocker, python_task, offers):
    driver = mocker.Mock()
    sched = BaseScheduler(name='test-scheduler')

    result = sched.submit(python_task)
    sched.on_offers(driver, offers)

    sched.on_update(driver, python_task.status('TASK_RUNNING'))
    assert result.state == 'TASK_RUNNING'
    assert result.ready() == False

    sched.on_update(driver, python_task.status('TASK_FINISHED',
                                               result=python_task()))
    assert result.state == 'TASK_FINISHED'
    assert result.ready() == True
    assert result.successful() == True
    assert result.get() == 10
