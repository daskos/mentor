from mesos.interface import mesos_pb2
from satyr.proxies import SchedulerDriverProxy, SchedulerProxy
from satyr.proxies.messages import (ExecutorID, OfferID, Operation, Request,
                                    SlaveID, TaskInfo, TaskStatus)


def test_scheduler_event_handlers(mocker):
    sched = mocker.Mock()
    driver = mocker.Mock()
    proxy = SchedulerProxy(sched)

    proxy.executorLost(driver, mesos_pb2.ExecutorInfo(),
                       mesos_pb2.ExecutorID(), 1)
    proxy.frameworkMessage(driver, mesos_pb2.ExecutorID(),
                           mesos_pb2.SlaveID(), 'message')
    proxy.offerRescinded(driver, mesos_pb2.OfferID())
    proxy.registered(driver, mesos_pb2.FrameworkID(), mesos_pb2.MasterInfo())
    proxy.resourceOffers(driver, [mesos_pb2.Offer(), mesos_pb2.Offer()])
    proxy.slaveLost(driver, mesos_pb2.SlaveID())
    proxy.statusUpdate(driver, mesos_pb2.TaskStatus())
    proxy.reregistered(driver, mesos_pb2.MasterInfo())
    proxy.error(driver, 'message')
    proxy.disconnected(driver)

    sched.on_executor_lost.assert_called_once()
    sched.on_message.assert_called_once()
    sched.on_rescinded.assert_called_once()
    sched.on_registered.assert_called_once()
    sched.on_offers.assert_called_once()
    sched.on_slave_lost.assert_called_once()
    sched.on_update.assert_called_once()
    sched.on_reregistered.assert_called_once()
    sched.on_error.assert_called_once()
    sched.on_disconnected.assert_called_once()


def test_scheduler_driver_callbacks(mocker):
    driver = mocker.Mock()
    proxy = SchedulerDriverProxy(driver)

    proxy.abort()
    proxy.join()
    proxy.start()
    proxy.stop()
    proxy.acknowledge(TaskStatus())
    proxy.decline(OfferID())
    proxy.kill(OfferID())
    proxy.launch(OfferID(), [TaskInfo()])
    proxy.message(ExecutorID(), SlaveID(), 'message')
    proxy.reconcile([TaskStatus()])
    proxy.request([Request()])
    proxy.revive()
    proxy.suppress()
    proxy.accept(OfferID(), [Operation()])

    driver.abort.assert_called_once()
    driver.join.assert_called_once()
    driver.start.assert_called_once()
    driver.stop.assert_called_once()
    driver.acknowledgeStatusUpdate.assert_called_once()
    driver.declineOffer.assert_called_once()
    driver.killTask.assert_called_once()
    driver.launchTasks.assert_called_once()
    driver.sendFrameworkMessage.assert_called_once()
    driver.reconcileTasks.assert_called_once()
    driver.requestResources.assert_called_once()
    driver.reviveOffers.assert_called_once()
    driver.suppressOffers.assert_called_once()
    driver.acceptOffers.assert_called_once()
