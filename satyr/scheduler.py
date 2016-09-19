from __future__ import absolute_import, division, print_function

import logging
import os
import time
from collections import Counter
from functools import partial

from mesos.native import MesosSchedulerDriver

from .constraint import pour
from .interface import Scheduler
from .placement import bfd
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


# TODO reuse the same type of executors
class Framework(Scheduler):

    def __init__(self, constraint=pour, placement=partial(bfd, cpus=1, mem=1)):
        self.healthy = True
        self.tasks = {}      # holds task_id => task pairs
        self.placement = placement
        self.constraint = constraint

    @property
    def statuses(self):
        return {task_id: task.status for task_id, task in self.tasks.items()}

    # @property
    # def executors(self):
    #     tpls = (((task.slave_id, task.executor.id), task)
    #             for task_id, task in self.tasks.items())
    #     return {k: list(v) for k, v in groupby(tpls)}

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

        # query tasks ready for scheduling
        staging = [self.tasks[status.task_id]
                   for status in self.statuses.values() if status.is_staging()]

        # filter acceptable offers
        accepts, declines = self.constraint(offers)

        # best-fit-decreasing binpacking
        bins, skip = self.placement(staging, accepts)

        # reject offers not met constraints
        for offer in declines:
            driver.decline(offer.id)

        # launch tasks
        for offer, tasks in bins:
            try:
                for task in tasks:
                    task.slave_id = offer.slave_id
                    task.status.state = 'TASK_STARTING'
                # running with empty task list will decline the offer
                logging.info('launches {}'.format(tasks))
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


# backward compatibility
QueueScheduler = Framework


if __name__ == '__main__':
    scheduler = QueueScheduler()
    with SchedulerDriver(scheduler, name='test') as fw:
        scheduler.wait()
