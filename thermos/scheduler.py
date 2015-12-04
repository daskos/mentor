from mesos.interface import Scheduler, mesos_pb2
from mesos.native import MesosSchedulerDriver
from collections import deque
from threading import Thread
from event_handlers import resource_offer_handler, status_update_handler
from skeleton import Skeleton, create_driver_method
import os


class ThermosScheduler(Scheduler, Skeleton):
    ALLOWED_HANDLERS = ['resourceOffers', 'statusUpdate', 'frameworkMessage']

    config = {'resources': {'cpus': 1, 'mem': 512}, 'max_tasks': 10, 'name': 'Thermos'}
    task_stats = {'running': 0, 'successful': 0, 'failed': 0, 'created': 0}
    driver_states = {'is_starting': True}

    def __init__(self, config, task_executor):
        print 'Starting framework [%s]' % config['name']
        self.config.update(config)
        self.task_executor = task_executor
        self.name = config['name']
        self.task_queue = deque()


def create_framework(config):
    framework = mesos_pb2.FrameworkInfo()
    framework.user = config.get('user', '')
    framework.name = config['name']
    return framework


def create_task_executor(config):
    path = os.path.join(config['executor_dir'], config.get('executor_file', 'executor.py'))

    executor = mesos_pb2.ExecutorInfo()
    executor.name = config['name']
    executor.executor_id.value = config['id']
    executor.command.value = 'python %s' % path

    uri = executor.command.uris.add()
    uri.value = path
    uri.extract = False

    return executor


def create_scheduler(config, executor_message_handler, task='message'):
    scheduler = ThermosScheduler(config, create_task_executor(config))
    scheduler.add_handler('frameworkMessage', executor_message_handler)
    scheduler.add_handler('resourceOffers', resource_offer_handler)
    scheduler.add_handler('statusUpdate', status_update_handler)
    scheduler.task_queue.append(task)
    return MesosSchedulerDriver(scheduler, create_framework(config), config['master'])


def run_scheduler(scheduler):
    framework_thread = Thread(target=create_driver_method(scheduler), args=())
    framework_thread.start()
