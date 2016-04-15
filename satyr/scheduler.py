from __future__ import absolute_import, division, print_function

import atexit

from mesos.interface import mesos_pb2
from mesos.native import MesosSchedulerDriver

from . import log as logging
from .interface import Scheduler
from .proxies import SchedulerProxy
from .proxies.messages import FrameworkInfo, encode


class AsyncResult(object):

    def __init__(self, state):
        self.state = state

    def get(self, timeout=None):
        if self.ready():
            return self.value
        else:
            raise ValueError('Async result not ready!')

    def wait(self, timeout=None):
        # block intil ready
        pass

    def ready(self):
        return self.state not in ['TASK_STAGING', 'TASK_RUNNING']

    def successful(self):
        return self.state in ['TASK_FINISHED']


class BaseScheduler(Scheduler):

    # TODO envargs
    def __init__(self, name, user='', master='zk://localhost:2181/mesos',
                 *args, **kwargs):
        self.framework = FrameworkInfo(name=name, user=user, **kwargs)
        self.master = master
        self.tasks = deque()
        self.results = {}

    def __call__(self):
        return self.run()

    def run(self):
        # TODO logging
        # TODO implicit aknoladgements

        driver = MesosSchedulerDriver(SchedulerProxy(self),
                                      encode(self.framework),
                                      self.master)
        atexit.register(driver.stop)

        # run things
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()  # Ensure that the driver process terminates.
        return status

    def submit(fn, args=[], kwargs={}, **kwds):
        task = PythonTask(fn=fn, args=args, kwargs=kwargs, **kwds)
        self.tasks.append(task)
        self.results[task.id.value] = AsyncResult(task.state)
        return self.results[task.id.value]

    def on_offers(self, driver, offers):  # default binpacking
        try:
            task = self.tasks.pop()
        except:
            pass
        else:
            launched = False
            for offer in offers:
                if offer > task:
                    task.slave_id = offer.slave_id
                    driver.launch(offer.id, [task])
                    launched = True
                else:
                    driver.decline(offer.id)
            if not launched:
                self.tasks.append(task)

    def on_update(self, driver, status):
        result = self.results[status.task_id.value]
        result.state = status.state

        if status.state == 'TASK_FINISHED':
            result.value = status.result
            self.results.pop(status.task_id.value)
        elif status.state in ['TASK_FAILED', 'TASK_LOST', 'TASK_KILLED']:
            self.results.pop(status.task_id.value)

        if len(self.tasks) == 0 and len(self.results) == 0:
            driver.stop()


if __name__ == '__main__':
    from .utils import run_daemon

    scheduler = BaseScheduler(name='Base')
    run_daemon('Scheduler Process', scheduler)
