import pytest

from mesos.interface import mesos_pb2
from satyr.proxies import SchedulerProxy, SchedulerDriverProxy


def test_event_handlers_with_wrapped_arguments(mocker):
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
