from __future__ import absolute_import, division, print_function

import atexit
import logging
import os
import signal
import time
from collections import Counter

from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver

from .binpack import bfd
from .interface import Scheduler
from .proxies import SchedulerProxy
from .proxies.messages import FrameworkInfo, TaskInfo, encode
from .utils import timeout


class Running(object):

    def __init__(self, scheduler, name, user='', master=os.getenv('MESOS_MASTER'),
                 implicit_acknowledge=1, *args, **kwargs):
        scheduler = SchedulerProxy(scheduler)
        framework = FrameworkInfo(name=name, user=user, *args, **kwargs)
        self.driver = MesosSchedulerDriver(scheduler, encode(framework),
                                           master, implicit_acknowledge)

        def shutdown(signal, frame):
            self.stop()

        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
        atexit.register(self.stop)

    def run(self):
        return self.driver.run()

    def start(self):
        status = self.driver.start()
        assert status == mesos_pb2.DRIVER_RUNNING
        return status

    def stop(self):
        return self.driver.stop()

    def join(self):
        return self.driver.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.join()
        if exc_type:
            raise exc_type, exc_value, traceback


class QueueScheduler(Scheduler):

    # todo remove statuses or replace as a property wich plucks status from
    # tasks
    def __init__(self, *args, **kwargs):
        self.tasks = {}    # holding task_id => (task, status, result) pairs

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
            while not self.is_idle():
                time.sleep(0.1)

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
                driver.launch(offer.id, tasks)
            except Exception:
                logging.exception('Exception occured during task launch!')

    def on_update(self, driver, status):
        task = self.tasks[status.task_id]
        logging.info('Updated task {} state {}'.format(status.task_id,
                                                       status.state))
        if status.has_terminated():
            del self.tasks[task.id]
            if status.has_failed():
                logging.error('Aborting because task {} is in unexpected state '
                              '{} with message {}'.format(status.task_id,
                                                          status.state,
                                                          status.message))
                driver.abort()

        task.update(status)
        self.report()


if __name__ == '__main__':
    scheduler = QueueScheduler()
    with Running(scheduler, name='test') as fw:
        scheduler.wait()
