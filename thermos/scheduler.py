from mesos.interface import Scheduler, mesos_pb2
from mesos.native import MesosSchedulerDriver
from collections import deque
from threading import Thread
from event_handlers import resource_offer_handler, status_update_handler
from skeleton import Skeleton, create_driver_method
import os


class ThermosScheduler(Scheduler, Skeleton):
    ALLOWED_HANDLERS = ['resource_offers', 'status_update', 'framework_message']

    config = {'resources': {'cpus': 1, 'mem': 512}, 'max_tasks': 10, 'name': 'Thermos'}
    task_stats = {'running': 0, 'successful': 0, 'failed': 0, 'created': 0}
    driver_states = {'is_starting': True}

    def __init__(self, config={}):
        print 'Starting framework [%s]' % name
        self.config.update(config)
        self.name = config['name']
        self.task_queue = deque()


def create_framework(config):
    framework = mesos_pb2.FrameworkInfo()
    framework.user = config.get('user', '')
    framework.name = config['name']
    return framework


def create_task_executor(config):
    executor = mesos_pb2.ExecutorInfo()
    executor.name = name
    executor.executor_id.value = name
    executor.command.value = 'python %s' % config['executor_dir']

    uri = executor.command.uris.add()
    uri.value = os.path.join(config['executor_dir'], config.get('executor_file', 'executor.py'))
    uri.extract = False

    return executor


def create_scheduler(config, executor_message_handler):
    scheduler = ThermosScheduler(config=config, create_task_executor(config))
    scheduler.add_handler('framework_message', executor_message_handler)
    scheduler.add_handler('resource_offers', resource_offer_handler)
    scheduler.add_handler('status_update', status_update_handler)
    return MesosSchedulerDriver(scheduler, create_framework(config), config['master'])


def run_scheduler(scheduler):
    framework_thread = Thread(target=create_driver_method(scheduler), args=())
    framework_thread.start()
