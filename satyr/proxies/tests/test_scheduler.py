import pytest

from mesos.interface import mesos_pb2
from satyr.proxies import SchedulerProxy, SchedulerDriverProxy

# TODO
def test_call_event_handlers(mocker):
    mocker.patch('satyr.proxies.scheduler.Map')

    sched = mocker.Mock()
    driver = mocker.Mock()

    proxy = SchedulerProxy(sched)

    proxy.disconnected(driver)
    proxy.reregistered(driver, mesos_pb2.MasterInfo())
    proxy.executorLost(driver, mesos_pb2.ExecutorInfo(), mesos_pb2.ExecutorID(), 1)

    sched.on_disconnected.assert_called_once()
    sched.on_reregistered.assert_called_once()
    sched.on_executor_lost.assert_called_once()
