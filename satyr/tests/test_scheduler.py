import pytest
from satyr.proxies.messages import CommandInfo, Cpus, Mem, TaskID, TaskInfo
from satyr.scheduler import Scheduler


class SingleTaskScheduler(Scheduler):

    def __init__(self, task, *args, **kwargs):
        self.ready = task
        self.running = None
        super(SingleTaskScheduler, self).__init__(*args, **kwargs)

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
def task():
    task = TaskInfo(name='test-task',
                    task_id=TaskID(value='test-task-id'),
                    resources=[Cpus(0.1), Mem(16)],
                    command=CommandInfo(value='echo 100'))
    return task


def test_state_transitions(mocker, task):
    sched = SingleTaskScheduler(name='test-scheduler', task=task)
    mocker.spy(sched, 'on_update')
    sched.run()

    calls = sched.on_update.call_args_list
    assert len(calls) == 2

    args, kwargs = calls[0]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_RUNNING'

    args, kwargs = calls[1]
    assert args[1].task_id.value == 'test-task-id'
    assert args[1].state == 'TASK_FINISHED'
