import cloudpickle
from .config import default as default_config
from . import scheduler


class Satyr():
    @property
    def queue(self):
        return self.sched.task_queue

    def __init__(self, sched):
        self.sched = sched
        self.framework_thread = scheduler.run_scheduler(sched)

    def apply_async(self, func, args=[], kwargs={}):
        task = {
            'resources': kwargs.get('resources', {}),
            'msg': cloudpickle.dumps({'func': func, 'args': args, 'kwargs': kwargs})
        }
        self.sched.add_job(task)


def create_satyr(config):
    config = dict(default_config, **config)
    sched  = scheduler.create_scheduler(config)

    return Satyr(sched)
