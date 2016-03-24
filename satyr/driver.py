import sys

from mesos.interface import mesos_pb2


def run(driver):
    status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
    driver.stop()
    sys.exit(status)
