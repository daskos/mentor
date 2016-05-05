from __future__ import absolute_import, division, print_function

import logging
import sys

from mesos.interface import Scheduler

from .messages import Filters, decode, encode


class SchedulerProxy(Scheduler):

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def registered(self, driver, frameworkId, masterInfo):
        logging.info("Registered with master", extra=dict())
        return self.scheduler.on_registered(SchedulerDriverProxy(driver),
                                            decode(frameworkId),
                                            decode(masterInfo))

    def reregistered(self, driver, masterInfo):
        logging.info("Re-registered with master", extra=dict())
        return self.scheduler.on_reregistered(SchedulerDriverProxy(driver),
                                              decode(masterInfo))

    def disconnected(self, driver):
        logging.debug("Disconnected from master")
        return self.scheduler.on_disconnected(SchedulerDriverProxy(driver))

    def resourceOffers(self, driver, offers):
        logging.debug("Got resource offers",
                      extra=dict(num_offers=len(offers)))
        return self.scheduler.on_offers(SchedulerDriverProxy(driver),
                                        map(decode, offers))

    def offerRescinded(self, driver, offerId):
        logging.debug('Offer rescinded', extra=dict(offer_id=offerId))
        return self.scheduler.on_rescinded(SchedulerDriverProxy(driver),
                                           decode(offerId))

    def statusUpdate(self, driver, status):
        logging.debug('Status update received', extra=dict(
            state=status.state, description=status.message))
        return self.scheduler.on_update(SchedulerDriverProxy(driver),
                                        decode(status))

    def frameworkMessage(self, driver, executorId, slaveId, message):
        logging.debug('Framework message received')
        return self.scheduler.on_message(SchedulerDriverProxy(driver),
                                         decode(executorId),
                                         decode(slaveId),
                                         message)

    def slaveLost(self, driver, slaveId):
        logging.debug('Slave has been lost, tasks should be rescheduled')
        return self.scheduler.on_slave_lost(SchedulerDriverProxy(driver),
                                            decode(slaveId))

    def executorLost(self, driver, executorId, slaveId, status):
        logging.debug('Executor has been lost')
        return self.scheduler.on_executor_lost(SchedulerDriverProxy(driver),
                                               decode(executorId),
                                               decode(slaveId),
                                               status)

    def error(self, driver, message):
        print("Error from Mesos: %s " % message, file=sys.stderr)
        return self.scheduler.on_error(SchedulerDriverProxy(driver), message)


class SchedulerDriverProxy(object):
    """Proxy Interface for Mesos scheduler drivers."""

    def __init__(self, driver):
        self.driver = driver

    def start(self):
        """Starts the scheduler driver.

        This needs to be called before any other driver calls are made.
        """
        return self.driver.start()

    def stop(self, failover=False):
        """Stops the scheduler driver.

        If the 'failover' flag is set to False then it is expected that this
        framework will never reconnect to Mesos and all of its executors and
        tasks can be terminated.  Otherwise, all executors and tasks will
        remain running (for some framework specific failover timeout) allowing
        the scheduler to reconnect (possibly in the same process, or from a
        different process, for example, on a different machine.)
        """
        return self.driver.stop(failover)

    def abort(self):
        """Aborts the driver so that no more callbacks can be made to the
           scheduler.

        The semantics of abort and stop have deliberately been separated so that
        code can detect an aborted driver (i.e., via the return status of
        SchedulerDriver.join), and instantiate and start another driver if
        desired (from within the same process.)
        """
        return self.driver.abort()

    def join(self):
        """Waits for the driver to be stopped or aborted, possibly blocking the
           current thread indefinitely.

        The return status of this function can be used to determine if the
        driver was aborted (see mesos.proto for a description of Status).
        """
        return self.driver.join()

    def request(self, requests):
        """Requests resources from Mesos.

        (see mesos.proto for a description of Request and how, for example, to
        request resources from specific slaves.)

        Any resources available are offered to the framework via
        Scheduler.resourceOffers callback, asynchronously.
        """
        return self.driver.requestResources(map(encode, requests))

    def launch(self, offer_id, tasks, filters=Filters()):
        """Launches the given set of tasks.

        Any resources remaining (i.e., not used by the tasks or their executors)
        will be considered declined.
        The specified filters are applied on all unused resources (see
        mesos.proto for a description of Filters). Available resources are
        aggregated when multiple offers are provided. Note that all offers must
        belong to the same slave. Invoking this function with an empty
        collection of tasks declines the offers in entirety (see
        Scheduler.decline).

        Note that passing a single offer is also supported.
        """
        return self.driver.launchTasks(encode(offer_id),
                                       map(encode, tasks),
                                       encode(filters))

    def kill(self, task_id):
        """Kills the specified task.

        Note that attempting to kill a task is currently not reliable.
        If, for example, a scheduler fails over while it was attempting to kill
        a task it will need to retry in the future.
        Likewise, if unregistered / disconnected, the request will be dropped
        (these semantics may be changed in the future).
        """
        return self.driver.killTask(encode(task_id))

    def reconcile(self, statuses):
        """Allows the framework to query the status for non-terminal tasks.

        This causes the master to send back the latest task status for each task
        in 'statuses', if possible. Tasks that are no longer known will result
        in a TASK_LOST update. If statuses is empty, then the master will send
        the latest status for each task currently known.
        """
        return self.driver.reconcileTasks(map(encode, statuses))

    def decline(self, offer_id, filters=Filters()):
        """Declines an offer in its entirety and applies the specified
           filters on the resources (see mesos.proto for a description of
           Filters).

        Note that this can be done at any time, it is not necessary to do this
        within the Scheduler::resourceOffers callback.
        """
        return self.driver.declineOffer(encode(offer_id),
                                        encode(filters))  # TODO filters

    def accept(self, offer_ids, operations, filters=Filters()):
        """Accepts the given offers and performs a sequence of operations
           on those accepted offers.

        See Offer.Operation in mesos.proto for the set of available operations.
        Available resources are aggregated when multiple offers are provided.

        Note that all offers must belong to the same slave. Any unused resources
        will be considered declined. The specified filters are applied on all
        unused resources (see mesos.proto for a description of Filters).
        """
        return self.driver.acceptOffers(map(encode, offer_ids),
                                        map(encode, operations),
                                        encode(filters))

    def revive(self):
        """Removes all filters previously set by the framework (via
           launchTasks()).

        This enables the framework to receive offers from those filtered slaves.
        """
        return self.driver.reviveOffers()

    def suppress(self):
        """Inform Mesos master to stop sending offers to the framework.

        The scheduler should call reviveOffers() to resume getting offers.
        """
        return self.driver.suppressOffers()

    def acknowledge(self, status):
        """Acknowledges the status update.

        This should only be called once the status update is processed durably
        by the scheduler.

        Not that explicit acknowledgements must be requested via the constructor
        argument, otherwise a call to this method will cause the driver to
        crash.
        """
        return self.driver.acknowledgeStatusUpdate(encode(status))

    def message(self, executor_id, slave_id, message):
        """Sends a message from the framework to one of its executors.

        These messages are best effort; do not expect a framework message to be
        retransmitted in any reliable fashion.
        """
        return self.driver.sendFrameworkMessage(encode(executor_id),
                                                encode(slave_id),
                                                message)
