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
            self.driver.stop()
        signal.signal(signal.SIGINT, shutdown)
        signal.signal(signal.SIGTERM, shutdown)
        atexit.register(self.driver.stop)

    def run(self):
        return self.driver.run()

    def start(self):
        status = self.driver.start()
        assert status == mesos_pb2.DRIVER_RUNNING
        return status

    def stop(self):
        logging.info("Stopping Mesos driver")
        self.driver.stop()
        logging.info("Joining Mesos driver")
        result = self.driver.join()
        logging.info("Joined Mesos driver")
        if result != mesos_pb2.DRIVER_STOPPED:
            raise RuntimeError("Mesos driver failed with %i", result)

    def join(self):
        return self.driver.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()


class AsyncResult(object):

    def __init__(self):
        self.success = None
        self.value = None

    def get(self, timeout=60):
        self.wait(timeout)
        if self.successful():
            return self.value
        else:
            try:
                raise self.value
            except TypeError:
                raise ValueError('Async result indicate task failed!')

    def wait(self, seconds=60):
        with timeout(seconds):
            while not self.ready():
                time.sleep(0.1)

    def ready(self):
        return self.success is not None

    def successful(self):
        return self.success is True


class QueueScheduler(Scheduler):

    def __init__(self, *args, **kwargs):
        self.tasks = {}    # holding task_id => (task, status, result) pairs
        self.results = {}
        self.statuses = {}

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
        self.statuses[task.id] = task.status('TASK_STAGING')
        self.results[task.id] = AsyncResult()
        return self.results[task.id]

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
                    self.statuses[task.id] = task.status('TASK_STARTING')

                # running with empty task list will decline the offer
                logging.info('launched tasks: {}'.format(
                    ', '.join(map(str, tasks))))
                driver.launch(offer.id, tasks)

                self.report()
            except Exception:
                logging.exception('Exception occured during task launch!')

    def on_update(self, driver, status):
        self.statuses[status.task_id] = status
        task = self.tasks[status.task_id]

        logging.info('Updated task {} state {}'.format(
            status.task_id, status.state))
        self.report()

        if status.has_terminated():
            result = self.results[task.id]
            result.success = status.has_succeeded()
            result.value = status.data

            del self.tasks[task.id]
            del self.results[task.id]
            del self.statuses[task.id]

        task.update(status)


if __name__ == '__main__':
    scheduler = QueueScheduler()
    with Running(scheduler, name='test') as fw:
        scheduler.wait()
