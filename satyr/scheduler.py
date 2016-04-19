from __future__ import absolute_import, division, print_function

import atexit
import logging
import os
import time
from collections import deque

from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver

from .interface import Scheduler
from .messages import PythonTaskStatus
from .proxies import SchedulerProxy
from .proxies.messages import FrameworkInfo, TaskInfo, encode


class PackError(Exception):
    pass


class BaseScheduler(Scheduler):

    # TODO envargs
    def __init__(self, name, user='', master=os.getenv('MESOS_MASTER'),
                 *args, **kwargs):
        self.framework = FrameworkInfo(name=name, user=user, **kwargs)
        self.master = master
        self.queue = deque()  # holding unscheduled tasks
        self.running = {}  # holding task_id => task pairs

    def __call__(self):
        return self.run()

    def daemonize(self):
        run_daemon('Scheduler Process', self)

    def run(self):
        # TODO logging
        # TODO implicit aknoladgements
        implicit_acknowledge = 1

        driver = MesosSchedulerDriver(SchedulerProxy(self),
                                      encode(self.framework),
                                      self.master,
                                      implicit_acknowledge)
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        return status

    def submit(self, task):  # supports commandtask, pythontask etc.
        assert isinstance(task, TaskInfo)
        self.queue.append(task)

    def on_offers(self, driver, offers):  # binpacking should be the default
        def pack(task, offers):
            for offer in offers:
                if offer >= task:
                    task.slave_id = offer.slave_id
                    return (offer, task)
            raise PackError('Couldn\'t pack')

        try:
            # should consider the whole queue as a list with a bin packing
            # solver
            task = self.queue.pop()
            offer, task = pack(task, offers)
        except PackError as e:
            # should reschedule if any error occurs at launch too
            self.tasks.append(task)
        except IndexError as e:
            # log empty queue
            pass
        else:
            offers.pop(offers.index(offer))
            driver.launch(offer.id, [task])
            self.running[task.id] = task
        finally:
            for offer in offers:
                driver.decline(offer.id)

    def on_update(self, driver, status):
        try:
            if status.is_terminated():
                task = self.running.pop(status.task_id)
            else:
                task = self.running[status.task_id]

            task.update(status)
        except:
            raise

        if len(self.queue) == 0 and len(self.running) == 0:
            driver.stop()


if __name__ == '__main__':
    from .utils import run_daemon

    scheduler = BaseScheduler(name='Base')
    scheduler.daemonize()
