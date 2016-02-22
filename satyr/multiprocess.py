import cloudpickle, uuid, copy
from time import sleep
from mesos.interface import mesos_pb2
from multiprocessing.pool import AsyncResult
from .config import default as default_config
from . import scheduler


class Satyr():
    @property
    def queue(self):
        return self.sched.task_queue

    def __init__(self, sched):
        self.result_pool = {}
        self.sched = sched
        self.sched.satyr = self
        self.async_results = {}
        self.results = {}
        scheduler.run_scheduler(self.sched)

    def apply_async(self, func, args=[], kwargs={}):
        task = {
            'id': str(uuid.uuid4()),
            'resources': kwargs.pop('resources', {}),
            'image': kwargs.pop('image', None),
            'msg': cloudpickle.dumps({'func': func, 'args': args, 'kwargs': kwargs})
        }

        self.sched.add_job(task)
        self.async_results[task['id']] = SatyrAsyncResult(self, task)

        return self.async_results[task['id']]

    def update_task_status(self, task_status):
        id = task_status.task_id.value
        status = task_status.state

        if status == mesos_pb2.TASK_FINISHED: # 2
            self.async_results[id].update_status(task_status, True)
        elif status in [mesos_pb2.TASK_FAILED, mesos_pb2.TASK_LOST, mesos_pb2.TASK_KILLED]: # 3, 5, 4
            self.async_results[id].update_status(task_status, False)


def create_satyr(config):
    def store_result(sched, driver, executorId, slaveId, message):
        result = cloudpickle.loads(message)
        if result.get('response', False) and sched.satyr:
            sched.satyr.results[result['id']] = result['msg']
            sched.satyr.async_results[result['id']].flags += (SatyrAsyncResult.FLAG_READY,)

    sched  = scheduler.create_scheduler(config, store_result)

    return Satyr(sched)


class SatyrAsyncResult(AsyncResult):
    FLAG_READY = 0
    FLAG_SUCCESSFUL = 1

    def __init__(self, satyr, task):
        self.satyr = satyr
        self.task  = copy.copy(task)
        self.flags = ()

    def get(self, timeout=None):
        self.wait(timeout)
        return self.satyr.results.get(self.task['id'], None)

    def wait(self, timeout=None):
        while not self.ready():
            sleep(1)
            print '[%s] Waiting to get ready...' % self.task['id']

    def ready(self):
        return self.FLAG_READY in self.flags

    def successful(self):
        return self.FLAG_READY in self.flags and self.FLAG_SUCCESSFUL in self.flags

    def update_status(self, task, is_successful):
        if not self.task['id'] == task.task_id.value: return
        self.flags = self.flags + (self.FLAG_SUCCESSFUL,) if is_successful else self.flags
