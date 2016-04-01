from __future__ import absolute_import, division, print_function

from mesos.native import MesosSchedulerDriver
from mesos.interface import mesos_pb2
from .base import Scheduler
from .core import Framework
from .utils import catch, set_signals

import logging
import signal
import atexit
import time
import sys
import multiprocessing as mp


def run_driver_async():
    framework = Framework(name='test')
    scheduler = Scheduler()

    driver = MesosSchedulerDriver(scheduler, framework.encode(), 'zk://localhost:2181/mesos')
    atexit.register(driver.stop)

    # run things
    status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
    driver.stop()  # Ensure that the driver process terminates.
    sys.exit(status)


def main():
    exception_receiver, exception_sender = mp.Pipe(False)

    subproc = mp.Process(target=catch(run_driver_async, exception_sender),
                         kwargs=dict(),
                         name="Satyr Mesos Scheduler")
    subproc.start()
    set_signals(subproc)

    while True:
        if exception_receiver.poll():
            exception_receiver.recv()
            logging.error('Terminating child process because it raised an '
                          'exception', extra=dict(is_alive=subproc.is_alive()))
            break
        if not subproc.is_alive():
            logging.error('Mesos Scheduler died and didn\'t notify me of its '
                          'exception. This may be a code bug. Check logs.',
                          extra=dict())
            break
        # save cpu cycles by checking for subprocess failures less often
        time.sleep(1)

    subproc.terminate()
    sys.exit(1)


if __name__ == '__main__':
    main()
