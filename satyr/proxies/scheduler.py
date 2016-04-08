from __future__ import absolute_import, division, print_function


from .. import log as logging

from mesos.interface import Scheduler

# test these classes with mocking the wrapped ones

# TODO add logging to all methods
# decodes messages then forwards

from .messages import FrameworkID, MasterInfo, OfferID, TaskStatus, SlaveID, ExecutorID, Offer

class SchedulerProxy(Scheduler):

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def registered(self, driver, frameworkId, masterInfo):
        driver = SchedulerDriverProxy(driver)
        framework_id = FrameworkID(frameworkId)
        master = MasterInfo(masterInfo)
        return self.scheduler.on_registered(driver, framework_id, master)

    def reregistered(self, driver, masterInfo):
        driver = SchedulerDriverProxy(driver)
        master = MasterInfo(masterInfo)

        logging.info("Re-registered with master", extra=dict(
            master_pid=master.pid, master_hostname=master.hostname,
            master_id=master.id, master_ip=master.ip, master_port=master.port))

        return self.scheduler.on_reregistered(driver, master)

    def disconnected(self, driver):
        driver = SchedulerDriverProxy(driver)
        return self.scheduler.on_disconnected(driver)

    def resourceOffers(self, driver, offers):
        driver = SchedulerDriverProxy(driver)
        offers = map(Offer, offers)

        logging.debug("Got resource offers", extra=dict(num_offers=len(offers)))

        return self.scheduler.on_offers(driver, offers)

    def offerRescinded(self, driver, offerId):
        driver = SchedulerDriverProxy(driver)
        offer_id = OfferID(offerId)

        logging.debug('Offer rescinded', extra=dict(offer_id=offer_id))

        return self.scheduler.on_rescinded(driver, offer_id)

    def statusUpdate(self, driver, status):
        driver = SchedulerDriverProxy(driver)
        status = TaskStatus(status)

        return self.scheduler.on_update(driver, status)

    def frameworkMessage(self, driver, executorId, slaveId, message):
        driver = SchedulerDriverProxy(driver)
        executor_id = ExecutorID(executorId)
        slave_id = SlaveID(slaveId)
        return self.scheduler.on_message(self, driver, executor_id, slave_id,
                                         message)

    def slaveLost(self, driver, slaveId):
        driver = SchedulerDriverProxy(driver)
        slave_id = SlaveID(slaveId)
        return self.scheduler.on_slave_lost(driver, slave_id)

    def executorLost(self, driver, executorId, slaveId, status):
        driver = SchedulerDriverProxy(driver)
        executor_id = ExecutorID(executorId)
        slave_id = SlaveID(slaveId)
        return self.scheduler.on_executor_lost(driver, executor_id, slave_id,
                                               status)

    def error(self, driver, message):
        print("Error from Mesos: %s " % message, file=sys.stderr)
        driver = SchedulerDriverProxy(driver)
        return self.scheduler.on_error(driver, message)


# encode entities in every fn
class SchedulerDriverProxy(object):

    def __init__(self, driver):
        self.driver = driver

    def request(self, requests):
        """Requests resources from Mesos.

        (see mesos.proto for a description of Request and how, for example, to
        request resources from specific slaves.)

        Any resources available are offered to the framework via
        Scheduler.resourceOffers callback, asynchronously.
        """
        requests = [request.encode() for request in requests]
        return self.driver.requestResources(requests)

    def launch(self, offer_id, tasks, filters=None):
        """Launches the given set of tasks.

        Any resources remaining (i.e., not used by the tasks or their executors)
        will be considered declined.
        The specified filters are applied on all unused resources (see
        mesos.proto for a description of Filters). Available resources are
        aggregated when multiple offers are provided. Note that all offers must
        belong to the same slave. Invoking this function with an empty
        collection of tasks declines the offers in entirety (see
        Scheduler.declineOffer).

        Note that passing a single offer is also supported.
        """
        tasks = [task.encode() for task in tasks]
        filters = filters.encode()
        offerId = offer_id.encode()
        self.driver.launchTasks(offerId, tasks, filters)

    def kill(self, task_id):
        """Kills the specified task.

        Note that attempting to kill a task is currently not reliable.
        If, for example, a scheduler fails over while it was attempting to kill
        a task it will need to retry in the future.
        Likewise, if unregistered / disconnected, the request will be dropped
        (these semantics may be changed in the future).
        """
        taskId = task_id.encode()
        return self.driver.killTask(taskId)

    def reconcile(self, statuses):
        """Allows the framework to query the status for non-terminal tasks.

        This causes the master to send back the latest task status for each task
        in 'statuses', if possible. Tasks that are no longer known will result
        in a TASK_LOST update. If statuses is empty, then the master will send
        the latest status for each task currently known.
        """
        statuses = [status.encode() for status in statuses]
        return self.driver.reconcileTasks(statuses)

    def decline(self, offer_id, filters={}):
        """Declines an offer in its entirety and applies the specified
           filters on the resources (see mesos.proto for a description of
           Filters).

        Note that this can be done at any time, it is not necessary to do this
        within the Scheduler::resourceOffers callback.
        """
        offerId = offer_id.encode()
        filters = filters.encode()
        return self.driver.declineOffer(offerId, filters)  #TODO filters

    def accept(self, offer_ids, operations, filters=None):
        """Accepts the given offers and performs a sequence of operations
           on those accepted offers.

        See Offer.Operation in mesos.proto for the set of available operations.
        Available resources are aggregated when multiple offers are provided.

        Note that all offers must belong to the same slave. Any unused resources
        will be considered declined. The specified filters are applied on all
        unused resources (see mesos.proto for a description of Filters).
        """
        offerIds = [offer_id.encode() for offer_id in offer_ids]
        operations = [operation.encode() for operation in operations]
        filters = filters.encode()
        return self.driver.acceptOffers(offerIds, operations, filters)

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
        status = status.encode()
        return self.driver.acknowledgeStatusUpdate(status)

    def message(self, executor_id, slave_id, message):
        """Sends a message from the framework to one of its executors.

        These messages are best effort; do not expect a framework message to be
        retransmitted in any reliable fashion.
        """
        executorId = executor_id.encode()
        slaveId = slave_id.encode()
        return self.driver.sendFrameworkMessage(executorId, slaveId, message)
