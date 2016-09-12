from __future__ import absolute_import, division, print_function

import logging
import os
import time
from collections import Counter

from mesos.native import MesosSchedulerDriver

from .binpack import bfd
from .interface import Scheduler
from .proxies import SchedulerDriverProxy, SchedulerProxy
from .proxies.messages import FrameworkInfo, TaskInfo, encode
from .utils import Interruptable, timeout


class SchedulerDriver(SchedulerDriverProxy, Interruptable):

    def __init__(self, scheduler, name, user='', master=os.getenv('MESOS_MASTER'),
                 implicit_acknowledge=1, *args, **kwargs):
        framework = FrameworkInfo(name=name, user=user, *args, **kwargs)
        driver = MesosSchedulerDriver(SchedulerProxy(scheduler),
                                      encode(framework),
                                      master, implicit_acknowledge)
        super(SchedulerDriver, self).__init__(driver)


# TODO create a scheduler which is reusing the same type of executors

class QueueScheduler(Scheduler):

    def __init__(self, *args, **kwargs):
        self.tasks = {}  # holding task_id => task pairs
        self.healthy = True

    @property
    def statuses(self):
        return {task_id: task.status for task_id, task in self.tasks.items()}

    def is_idle(self):
        return not len(self.tasks)

    def report(self):
        states = [status.state for status in self.statuses.values()]
        counts = Counter(states)
        message = ', '.join(['{}: {}'.format(key, count)
                             for key, count in counts.items()])
        logging.info('Task states: {}'.format(message))

    def wait(self, seconds=-1):
        with timeout(seconds):
            try:
                while self.healthy and not self.is_idle():
                    time.sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                raise

    def submit(self, task):  # supports commandtask, pythontask etc.
        assert isinstance(task, TaskInfo)
        self.tasks[task.id] = task

    def on_offers(self, driver, offers):
        logging.info('Received offers: {}'.format(sum(offers)))
        self.report()

        # maybe limit to the first n tasks
        staging = [self.tasks[status.task_id]
                   for status in self.statuses.values() if status.is_staging()]
        # best-fit-decreasing binpacking
        bins, skip = bfd(staging, offers, cpus=1, mem=1)

        for offer, tasks in bins:
            try:
                for task in tasks:
                    task.slave_id = offer.slave_id
                    task.status.state = 'TASK_STARTING'
                # running with empty task list will decline the offer
                logging.info('lanunches {}'.format(tasks))
                driver.launch(offer.id, tasks)
            except Exception:
                logging.exception('Exception occured during task launch!')

    def on_update(self, driver, status):
        task = self.tasks[status.task_id]
        logging.info('Updated task {} state to {}'.format(status.task_id,
                                                          status.state))
        try:
            task.update(status)  # creates new task.status in case of retry
        except:
            self.healthy = False
            driver.stop()
            raise
        finally:
            if status.has_terminated():
                del self.tasks[task.id]

        self.report()


if __name__ == '__main__':
    scheduler = QueueScheduler()
    with SchedulerDriver(scheduler, name='test') as fw:
        scheduler.wait()
