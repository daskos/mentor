from __future__ import absolute_import, division, print_function

import atexit
import logging
import os
import signal
import time
from collections import deque

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
        self.queue = deque()  # holding unscheduled tasks
        self.running = {}  # holding task_id => task pairs
        self.results = {}  # holding task_id => async_result pairs

    def is_idle(self):
        return not len(self.queue) and not len(self.running)

    def wait(self):
        while not self.is_idle():
            time.sleep(0.1)

    def submit(self, task):  # supports commandtask, pythontask etc.
        assert isinstance(task, TaskInfo)
        result = AsyncResult()
        self.results[task.id] = result
        self.queue.append(task)
        return result

    def on_offers(self, driver, offers):
        bins, skip = bfd(self.queue, offers)

        # filter out empty bins
        # TODO: verify driver.launch declines in case of empty task list
        bins = [(offer, tasks) for offer, tasks in bins if len(tasks)]

        for offer, tasks in bins:
            try:
                for task in tasks:
                    task.slave_id = offer.slave_id
                driver.launch(offer.id, tasks)
            except Exception:  # error occured, log
                logging.error('Exception occured during task launch!')
            else:  # successfully launched tasks
                offers.remove(offer)  # the remaining ones will be declined
                for task in tasks:
                    self.queue.remove(task)
                    self.running[task.id] = task

        for offer in offers:
            driver.decline(offer.id)

    def on_update(self, driver, status):
        if status.has_terminated():
            task = self.running.pop(status.task_id)
            result = self.results.pop(status.task_id)
            result.value = status.data
            result.success = status.has_succeeded()
        else:
            task = self.running[status.task_id]

        task.update(status)


if __name__ == '__main__':
    scheduler = QueueScheduler()
    with Running(scheduler, name='test') as fw:
        scheduler.wait()
