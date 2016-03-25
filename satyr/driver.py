import sys

from mesos.interface import mesos_pb2

def set_signals(driver, ns):
    """Kill child processes on sigint or sigterm"""
    def kill_children(signal, frame):
        #log.error(
        #    'Received a signal that is trying to terminate this process.'
        #    ' Terminating mesos and relay child processes!', extra=dict(
        #        mesos_framework_name=ns.mesos_framework_name,
        #        signal=signal))
        try:
            driver.terminate()
            # log.info(
            #     'terminated mesos scheduler',
            #    extra=dict(mesos_framework_name=ns.mesos_framework_name))
        except:
            pass
            #log.exception(
            #    'could not terminate mesos scheduler',
            #    extra=dict(mesos_framework_name=ns.mesos_framework_name))

        sys.exit(1)
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)


def run(driver):
    driver = MesosSchedulerDriver(self, framework_info(self.config), self.config['master'])
    framework_thread = Thread(target=run(driver), args=())
    framework_thread.start()

    status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
    driver.stop()
    sys.exit(status)
