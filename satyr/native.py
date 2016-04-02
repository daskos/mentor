from __future__ import absolute_import, division, print_function

import atexit
import signal
import sys
import multiprocessing as mp
import logging

from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver, MesosExecutorDriver

from .primitives import Framework
from .proxies import SchedulerProxy, ExecutorProxy


class Scheduler(object):

    def __init__(self, name, user='', master='zk://localhost:2181/mesos',
                 *args, **kwargs):
        self.framework = Framework(name=name, user=user, *args, **kwargs)
        self.master = master

    def __call__(self, *args, **kwargs):
        return self.run()  # TODO pass args

    def run(self):
        # TODO implicit aknoladgements
        driver = MesosSchedulerDriver(SchedulerProxy(self),
                                      self.framework.encode(),
                                      self.master)
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        sys.exit(status)

    def on_registered(self, driver, framework_id, master_info): pass
    def on_reregistered(self, driver, framework_id, master_info): pass
    def on_disconnected(self, driver): pass
    def on_offers(self, driver, offers): pass
    def on_rescinded(driver, offer_id): pass
    def on_update(self, driver, status): pass
    def on_message(self, driver, executor_id, slave_id, message): pass
    def on_slave_lost(self, driver, slave_id): pass
    def on_executor_lost(self, driver, executor_id, slave_id, status): pass
    def on_error(self, driver, message): pass


class Executor(ExecutorProxy):

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return self.run()  # TODO pass args

    def run(self):
        # TODO implicit aknoladgements
        driver = MesosExecutorDriver(ExecutorProxy(self))
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        sys.exit(status)


    def on_registered(self, driver, executor_info, framework_info, slave_info):
        pass

    def on_reregistered(self, driver, slave_info): pass
    def on_disconnected(self, driver): pass
    def on_message(self, driver, message): pass
    def on_launch(self, driver, task): pass
    def on_shutdown(self, driver): pass
    def on_error(self, driver, message): pass
