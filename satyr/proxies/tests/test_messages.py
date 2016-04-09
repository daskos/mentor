import pytest

from mesos.interface import mesos_pb2
from satyr.proxies.messages import MessageProxy, FrameworkInfo, FrameworkID


def test_framework_info():
    message = mesos_pb2.FrameworkInfo(id=mesos_pb2.FrameworkID(value='test'))
    wrapped = FrameworkInfo.decode(message)

    assert isinstance(wrapped, MessageProxy)
    assert isinstance(wrapped, FrameworkInfo)
    assert isinstance(wrapped.id, MessageProxy)
    assert isinstance(wrapped.id, FrameworkID)
