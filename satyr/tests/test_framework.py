from __future__ import absolute_import, division, print_function

import atexit

import pytest
from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver
from satyr.interface import Scheduler
from satyr.proxies import SchedulerProxy
from satyr.proxies.messages import (CommandInfo, Cpus, FrameworkInfo, Mem,
                                    TaskID, TaskInfo, encode)


# system test comes here

# 1. scheduler executing command
# 2. scheduler executing pickled python task via python executor


class SingleTaskScheduler(Scheduler):

    def __init__(self, task, name, user='', master='zk://localhost:2181/mesos',
                 *args, **kwargs):
        self.framework = FrameworkInfo(name=name, user=user, **kwargs)
        self.ready = task
        self.running = None
        self.master = master

    def __call__(self):
        return self.run()

    def run(self):
        # TODO logging
        # TODO implicit aknoladgements

        driver = MesosSchedulerDriver(SchedulerProxy(self),
                                      encode(self.framework),
                                      self.master)
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        return status

    def on_offers(self, driver, offers):
        if self.ready:
            for offer in offers:
                if offer > self.ready:
                    self.ready.slave_id = offer.slave_id
                    driver.launch(offer.id, [self.ready])
                    self.running = self.ready
                    self.ready = None
                else:
                    driver.decline(offer.id)

    def on_update(self, driver, status):
        if status.state == 'TASK_FINISHED':
            self.running = None
        if not self.ready and not self.running:
            driver.stop()


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
                    resources=[Cpus(0.1), Mem(64)],
                    command=CommandInfo(value='echo 100'))
    task.container.type = 'DOCKER'
    task.container.docker.image = 'lensacom/satyr:latest'
    return task


def test_state_transitions(mocker, command):
    sched = SingleTaskScheduler(name='test-scheduler', task=command)
    mocker.spy(sched, 'on_update')
    # this is a system test
    # to unit test don't run it
    sched.run()
    # mock the driver, then call on_offers, on_update(running), on_update(finished)
    # watch driver.launch called, then driver.stop called
    # move this code to a system test e.g. test_framework.py testing executor,
    # scheduler simultaneusly

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_FINISHED'


def test_dockerized_state_transitions(mocker, docker_command):
    sched = SingleTaskScheduler(name='test-scheduler', task=docker_command)
    mocker.spy(sched, 'on_update')
    sched.run()

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-docker-task-id'
    assert args[1].state == 'TASK_FINISHED'
