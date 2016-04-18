from __future__ import absolute_import, division, print_function

import atexit

import pytest
from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver
from satyr.interface import Scheduler
from satyr.messages import PythonTask
from satyr.proxies import SchedulerProxy
from satyr.proxies.messages import (CommandInfo, Cpus, Disk, FrameworkInfo,
                                    Mem, TaskID, TaskInfo, encode)
from satyr.scheduler import BaseScheduler


# system test comes here

# 1. scheduler executing command
# 2. basescheduler executing pickled python task via python executor


@pytest.fixture
def command():
    task = TaskInfo(name='test-task',
                    task_id=TaskID(value='test-task-id'),
                    resources=[Cpus(0.1), Mem(16)],
                    command=CommandInfo(value='echo 100'))
    return task


@pytest.fixture
def docker_command():
    task = TaskInfo(name='testdocker--task',
                    task_id=TaskID(value='test-docker-task-id'),
                    resources=[Cpus(0.5), Mem(64)],
                    command=CommandInfo(value='echo 100'))
    task.container.type = 'DOCKER'
    task.container.docker.image = 'lensacom/satyr:latest'
    return task


@pytest.fixture
def docker_python():
    task = PythonTask(task_id=TaskID(value='test-python-task-id'),
                      fn=sum, args=[range(5)],
                      name='test-python-task-name',
                      resources=[Cpus(0.1), Mem(128), Disk(0)])
    return task


def test_command(mocker, command):
    sched = BaseScheduler(name='test-scheduler')
    mocker.spy(sched, 'on_update')
    sched.submit(command)
    sched.run()

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_docker_command(mocker, docker_command):
    sched = BaseScheduler(name='test-scheduler')
    mocker.spy(sched, 'on_update')
    sched.submit(docker_command)
    sched.run()

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_docker_python(mocker, docker_python):
    sched = BaseScheduler(name='test-scheduler')
    mocker.spy(sched, 'on_update')
    sched.submit(docker_python)
    sched.run()

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-python-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-python-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_docker_python_result(mocker, docker_python):
    sched = BaseScheduler(name='test-scheduler')
    result = sched.submit(docker_python)
    sched.run()

    assert result.get() == 10
