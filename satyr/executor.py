from __future__ import absolute_import, division, print_function

import atexit
import signal
import sys

from mesos.interface import mesos_pb2
from mesos.native import MesosExecutorDriver

from . import log as logging
from .proxies import ExecutorProxy
from .proxies.messages import encode


class Executor(object):

    """Base class for Mesos executors.

    Users' executors should extend this class to get default implementations of
    methods they don't override.
    """

    def __call__(self):
        return self.run()

    def run(self):
        # TODO logging
        driver = MesosExecutorDriver(ExecutorProxy(self))
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        sys.exit(status)

    def on_registered(self, driver, executor, framework, slave):
        """Event handler triggered when the executor driver has been able to
           successfully connect with Mesos.

        In particular, a scheduler can pass some data to its executors through
        the FrameworkInfo.ExecutorInfo's data field.

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        executor: Executor
            The unique identifier of the lost Mesos executor
        framework: Framework
            TODO: write docs
        slave: Salve
            TODO: write docs
        """
        pass

    def on_reregistered(self, driver, slave):
        """Event handler triggered when the executor re-registers with a
           restarted slave.

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        slave: Slave
            TODO: write docs
        """
        pass

    def on_disconnected(self, driver):
        """Event handler triggered when the executor becomes "disconnected" from
           the slave.

        (e.g., the slave is being restarted due to an upgrade)

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        """
        pass

    def on_launch(self, driver, task):
        """Event handler triggered when a task has been launched on this
           executor (initiated via Scheduler.launch).

        Note that this task can be realized with a thread, a process, or some
        simple computation, however, no other callbacks will be invoked on this
        executor until this callback has returned.

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        task: Task
            TODO: write docs
        """
        def run_task():
            driver.update(task.status('TASK_RUNNING'))

            try:
                result = task()
            except Exception as e:
                driver.update(task.status('TASK_FAILED', message=e.message))
            else:
                driver.update(task.status('TASK_FINISHED', data=result))

        thread = threading.Thread(target=run_task)
        thread.start()

    def on_kill(self, driver, task_id):
        """Event handler triggered when a task running within this executor has
           been killed (via SchedulerDriver.kill).

        Note that no status update will be sent on behalf of the executor, the
        executor is responsible for creating a new TaskStatus (i.e., with
        TASK_KILLED) and invoking ExecutorDriver's update method.

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        task_id: string
            Unique identifier of the killed task
        """
        pass

    def on_message(self, driver, message):
        """Event handler triggered when a framework message has arrived for this
           executor.

        These messages are best effort; do not expect a framework message to be
        retransmitted in any reliable fashion.

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        message: string
            Arbitrary byte stream
        """
        pass

    def on_shutdown(self, driver):
        """Event handler triggered when the executor should terminate all of its
           currently running tasks.

        Note that after Mesos has determined that an executor has terminated any
        tasks that the executor did not send terminal status updates for (e.g.,
        TASK_KILLED, TASK_FINISHED, TASK_FAILED, etc) a TASK_LOST status update
        will be created.

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        """
        pass

    def on_error(self, driver, message):
        """Event handler triggered when a fatal error has occurred with the
           executor and/or executor driver.

        The driver will be aborted BEFORE invoking this callback.

        Parameters
        ----------
        driver: ExecutorDriver
            Interface for interacting with Mesos Slave
        message: string
            Arbitrary byte stream
        """
        pass


if __name__ == '__main__':
    Executor().run()
