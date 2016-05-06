from __future__ import absolute_import, division, print_function

import logging
import sys

from mesos.interface import Executor

from .messages import decode, encode


class ExecutorProxy(Executor):
    """Base class for Mesos executors.

    Users' executors should extend this class to get default implementations of
    methods they don't override.
    """

    def __init__(self, executor):
        self.executor = executor

    def registered(self, driver, executorInfo, frameworkInfo, slaveInfo):
        logging.info('Registered with slave', extra=dict())
        return self.executor.on_registered(ExecutorDriverProxy(driver),
                                           decode(executorInfo),
                                           decode(frameworkInfo),
                                           decode(slaveInfo))

    def reregistered(self, driver, slaveInfo):
        logging.info('Re-registered with slave', extra=dict())
        return self.executor.on_reregistered(ExecutorDriverProxy(driver),
                                             decode(slaveInfo))

    def disconnected(self, driver):
        logging.info('Disconnected from slave')
        return self.executor.on_disconnected(ExecutorDriverProxy(driver))

    def launchTask(self, driver, taskInfo):
        logging.info('Launches task', extra=dict())
        return self.executor.on_launch(ExecutorDriverProxy(driver),
                                       decode(taskInfo))

    def killTask(self, driver, taskId):
        logging.info('Kills task', extra=dict())
        return self.executor.on_kill(ExecutorDriverProxy(driver),
                                     decode(taskId))

    def frameworkMessage(self, driver, message):
        logging.info('Recived framework message', extra=dict())
        return self.executor.on_message(ExecutorDriverProxy(driver),
                                        message)

    def shutdown(self, driver):
        logging.info('Executor shutdown')
        return self.executor.on_shutdown(ExecutorDriverProxy(driver))

    def error(self, driver, message):
        print("Error from Mesos: %s" % message, file=sys.stderr)
        return self.executor.on_error(ExecutorDriverProxy(driver),
                                      message)


class ExecutorDriverProxy(object):

    def __init__(self, driver):
        self.driver = driver

    def start(self):
        """Starts the executor driver.

        This needs to be called before any other driver calls are made.
        """
        logging.info('Driver started')
        return self.driver.start()

    def stop(self):
        """Stops the executor driver."""
        logging.info('Driver stopped')
        return self.driver.stop()

    def abort(self):
        """Aborts the driver so that no more callbacks can be made to the
           executor.

        The semantics of abort and stop have deliberately been separated so that
        code can detect an aborted driver (i.e., via the return status of
        ExecutorDriver.join), and instantiate and start another driver if
        desired (from within the same process, although this functionality is
        currently not supported for executors).
        """
        logging.info('Driver aborted')
        return self.driver.abort()

    def join(self):
        """Waits for the driver to be stopped or aborted, possibly blocking the
           current thread indefinitely.

        The return status of this function can be used to determine if the
        driver was aborted (see mesos.proto for a description of Status).
        """
        logging.info('Joined to driver')
        return self.driver.join()

    def run(self):
        """Starts and immediately joins (i.e., blocks on) the driver."""
        logging.info('Driver run')
        return self.driver.run()

    def update(self, status):
        """Sends a status update to the framework scheduler.

        Retrying as necessary until an acknowledgement has been received or the
        executor is terminated (in which case, a TASK_LOST status update will be
        sent).
        See Scheduler.statusUpdate for more information about status update
        acknowledgements.
        """
        logging.info('Executor sends status update')
        return self.driver.sendStatusUpdate(encode(status))

    def message(self, data):
        """Sends a message to the framework scheduler.

        These messages are best effort; do not expect a framework message to be
        retransmitted in any reliable fashion.
        """
        logging.info('Driver sends framework message')
        return self.driver.sendFrameworkMessage(data)
