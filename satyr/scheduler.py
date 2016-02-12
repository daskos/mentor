from mesos.interface import Scheduler, mesos_pb2
from mesos.native import MesosSchedulerDriver
from collections import deque
from threading import Thread
from event_handlers import resource_offer_handler, status_update_handler
from skeleton import Skeleton, create_driver_method
import os


class SatyrScheduler(Scheduler, Skeleton):
    ALLOWED_HANDLERS = ['resourceOffers', 'statusUpdate', 'frameworkMessage']

    config = {'resources': {'cpus': 1, 'mem': 512}, 'max_tasks': 10, 'name': 'Satyr'}
    task_stats = {'running': 0, 'successful': 0, 'failed': 0, 'created': 0}
    driver_states = {'is_starting': True}

    def __init__(self, config, task_executor):
        print 'Starting framework [%s]' % config['name']
        self.config.update(config)
        self.task_executor = task_executor
        self.name = config['name']
        self.task_queue = deque()

    def add_job(self, message):
        self.task_queue.append(message)

    def shutdown_if_done(self, driver):
        if not any((
                self.config.get('permanent'),
                self.driver_states['is_starting'],
                self.task_stats['running'],
                len(self.task_queue))):
            print 'We are finished.'
            self.force_shutdown()

    def force_shutdown(self):
        driver.stop()


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
    executor.command.value = config.get('command') or 'python %s' % config.get('executor_file', 'executor.py')

    uri = executor.command.uris.add()
    uri.value = path
    uri.extract = False

    return executor


def create_scheduler(config, executor_message_handler, job=None):
    scheduler = SatyrScheduler(config, create_task_executor(config))
    scheduler.add_handler('frameworkMessage', executor_message_handler)
    scheduler.add_handler('resourceOffers', resource_offer_handler)
    scheduler.add_handler('statusUpdate', status_update_handler)

    if not job is None:
        scheduler.add_job(job)

    return scheduler


def run_scheduler(scheduler):
    driver = MesosSchedulerDriver(scheduler, create_framework(scheduler.config), scheduler.config['master'])
    framework_thread = Thread(target=create_driver_method(driver), args=())
    framework_thread.start()
