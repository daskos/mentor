from __future__ import absolute_import, division, print_function

from protobuf_to_dict import protobuf_to_dict, dict_to_protobuf
from mesos.interface import Executor, ExecutorDriver, mesos_pb2

from .messages import ExecutorInfo, FrameworkInfo, SlaveInfo, TaskInfo, TaskID

# testing these are pretty straightforward

# decode entities in every fn
# TODO: logging
class ExecutorProxy(Executor):
    """Base class for Mesos executors.

    Users' executors should extend this class to get default implementations of
    methods they don't override.
    """

    def __init__(self, executor):
        self.executor = executor

    def registered(self, driver, executorInfo, frameworkInfo, slaveInfo):
        driver = ExecutorDriverProxy(driver)
        executor = ExecutorInfo(executorInfo)
        framework = FrameworkInfo(frameworkInfo)
        slave = SlaveInfo(slaveInfo)
        return self.executor.on_registered(driver, executor, framework, slave)

    def reregistered(self, driver, slaveInfo):
        driver = ExecutorDriverProxy(driver)
        slave = SlaveInfo(slaveInfo)
        return self.executor.on_reregistered(driver, slave)

    def disconnected(self, driver):
        driver = ExecutorDriverProxy(driver)
        return self.executor.on_disconnected(driver)

    def launchTask(self, driver, taskInfo):
        driver = ExecutorDriverProxy(driver)
        task = TaskInfo(taskInfo)
        return self.executor.on_launch(driver, task)

    def killTask(self, driver, taskId):
        driver = ExecutorDriverProxy(driver)
        task_id = TaskID(taskId)
        return self.executor.on_kill(driver, task_id)

    def frameworkMessage(self, driver, message):
        driver = ExecutorDriverProxy(driver)
        return self.executor.on_message(driver, message)

    def shutdown(self, driver):
        driver = ExecutorDriverProxy(driver)
        return self.executor.on_shutdown(driver)

    def error(self, driver, message):
        print("Error from Mesos: %s" % message, file=sys.stderr)
        driver = ExecutorDriverProxy(driver)
        return self.executor.on_error(driver, message)


class ExecutorDriverProxy(object):

    def __init__(self, driver):
        self.driver = driver

    def start(self):
        """Starts the executor driver.

        This needs to be called before any other driver calls are made.
        """
        return self.driver.start()

    def stop(self):
        """Stops the executor driver."""
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
        return self.driver.abort()

    def join(self):
        """Waits for the driver to be stopped or aborted, possibly blocking the
           current thread indefinitely.

        The return status of this function can be used to determine if the
        driver was aborted (see mesos.proto for a description of Status).
        """
        return self.driver.join()

    def run(self):
        """Starts and immediately joins (i.e., blocks on) the driver."""
        return self.driver.run()

    def update(self, status):
        """Sends a status update to the framework scheduler.

        Retrying as necessary until an acknowledgement has been received or the
        executor is terminated (in which case, a TASK_LOST status update will be
        sent).
        See Scheduler.statusUpdate for more information about status update
        acknowledgements.
        """
        status = status.encode()
        return self.driver.sendStatusUpdate(status)

    def message(self, data):
        """Sends a message to the framework scheduler.

        These messages are best effort; do not expect a framework message to be
        retransmitted in any reliable fashion.
        """
        return self.driver.sendFrameworkMessage(data)
