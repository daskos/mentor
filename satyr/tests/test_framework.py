from __future__ import absolute_import, division, print_function

import pytest
from satyr.messages import PythonTask
from satyr.proxies.messages import (CommandInfo, Cpus, Disk, Mem, TaskID,
                                    TaskInfo)
from satyr.scheduler import QueueScheduler, Running


@pytest.fixture
def command():
    task = TaskInfo(name='test-task',
                    id=TaskID(value='test-task-id'),
                    resources=[Cpus(0.1), Mem(16)],
                    command=CommandInfo(value='echo 100'))
    return task


@pytest.fixture
def docker_command():
    task = TaskInfo(name='test-docker-task',
                    id=TaskID(value='test-docker-task-id'),
                    resources=[Cpus(0.5), Mem(64)],
                    command=CommandInfo(value='echo 100'))
    task.container.type = 'DOCKER'
    task.container.docker.image = 'lensacom/satyr:latest'
    return task


@pytest.fixture
def docker_python():
    task = PythonTask(id=TaskID(value='test-python-task-id'),
                      fn=sum, args=[range(5)],
                      name='test-python-task-name',
                      resources=[Cpus(0.1), Mem(128), Disk(0)])
    return task


def test_command(mocker, command):
    sched = QueueScheduler()
    mocker.spy(sched, 'on_update')

    with Running(sched, name='test-scheduler'):
        sched.submit(command)
        sched.wait()  # block until all tasks finishes

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_docker_command(mocker, docker_command):
    sched = QueueScheduler()
    mocker.spy(sched, 'on_update')

    with Running(sched, name='test-scheduler'):
        sched.submit(docker_command)
        sched.wait()  # block until all tasks finishes

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_docker_python(mocker, docker_python):
    sched = QueueScheduler()
    mocker.spy(sched, 'on_update')

    with Running(sched, name='test-scheduler'):
        sched.submit(docker_python)
        sched.wait()  # block until all tasks finishes

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-python-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-python-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_docker_python_result(mocker, docker_python):
    sched = QueueScheduler()
    with Running(sched, name='test-scheduler'):
        sched.submit(docker_python)
        sched.wait()  # block until all tasks finishes

    assert docker_python.result == 10
