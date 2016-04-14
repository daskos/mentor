from __future__ import absolute_import, division, print_function

import atexit

from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver

from . import log as logging
from .interface import Scheduler
from .proxies import SchedulerProxy
from .proxies.messages import FrameworkInfo, encode


class BaseScheduler(Scheduler):

    # TODO envargs
    def __init__(self, name, user='', master='zk://localhost:2181/mesos',
                 *args, **kwargs):
        self.framework = FrameworkInfo(name=name, user=user, **kwargs)
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
        for offer in offers:
            logging.info('Offer {} declined'.format(offer.id))
            driver.decline(offer.id)


if __name__ == '__main__':
    from .utils import run_daemon

    scheduler = BaseScheduler(name='Base')
    run_daemon('Scheduler Process', scheduler)
