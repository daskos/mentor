from __future__ import absolute_import, division, print_function

import logging
import os
import time
from collections import Counter
from functools import partial


from mentor.constraint import pour
from mentos.interface import Scheduler
from mentor.placement import bfd
from mentor.messages import  TaskInfo,Offer,Message
from mentos.scheduler import SchedulerDriver
from mentor.utils import Interruptable, timeout

log = logging.getLogger(__name__)

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
        log.info('Task states: {}'.format(message))

    def wait(self, seconds=-1):
        with timeout(seconds):
            try:
                while self.healthy and not self.is_idle():
                    time.sleep(0.1)
            except (KeyboardInterrupt, SystemExit):
                raise

    def submit(self, task):  # supports commandtask, pythontask etc.
        assert isinstance(task, TaskInfo)
        self.tasks[task.task_id.value] = task

    def on_offers(self, driver, offers):
        offers = [Offer(f) for f in offers]
        log.info('Received offers: {}'.format(sum(offers)))
        self.report()

        # query tasks ready for scheduling
        staging = [self.tasks[status.task_id.value]
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
                    task.agent_id = offer.agent_id
                    task.status.state = 'TASK_STARTING'
                # running with empty task list will decline the offer
                    log.info('launches {}'.format(tasks))
                driver.launch(offer.id, tasks)
            except Exception as ex:
                log.exception('Exception occured during task launch!')

    def on_update(self, driver, status):
        #status = Message(**status)
        task = self.tasks[status.task_id.value]
        log.info('Updated task {} state to {}'.format(status.task_id,
                                                      status.state))
        try:
            task.update(status)  # creates new task.status in case of retry
        except Exception as ex:
            self.healthy = False
            driver.stop()
            raise
        finally:
            if status.has_terminated():
                del self.tasks[task.task_id.value]

        self.report()

    def on_outbound_success(self, driver, request):
        pass

    def on_outbound_error(self, driver, request, endpoint, error):
        pass


# backward compatibility
QueueScheduler = Framework


if __name__ == '__main__':
    import getpass
    sched = Framework()
    with SchedulerDriver(os.getenv('MESOS_MASTER') or "localhost", sched, "Queue", getpass.getuser()) as driver:
        sched.wait()
