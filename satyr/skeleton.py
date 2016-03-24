from __future__ import absolute_import, division, print_function

import sys
import types

from mesos.interface import mesos_pb2


class Skeleton(object):
    pass

def create_driver_method(driver):
    def method():
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()
        sys.exit(status)

    return method
