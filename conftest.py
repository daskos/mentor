import os

import pytest

zookeeper_host = os.environ.get('ZOOKEEPER_HOST')


@pytest.yield_fixture
def zk():
    pytest.importorskip('kazoo')
    pytest.mark.skipif(zookeeper_host is None,
                       reason='No ZOOKEEPER_HOST envar defined')

    from kazoo.client import KazooClient
    zk = KazooClient(hosts=zookeeper_host)
    try:
        zk.start()
        yield zk
    finally:
        zk.delete('/satyr', recursive=True)
        zk.stop()
