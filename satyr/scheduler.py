from mesos.interface import Scheduler
from mesos.native import MesosSchedulerDriver
from threading import Thread
import os

from .event_handlers import ResourceOfferHandler, StatusUpdateHandler
from .skeleton import Skeleton, create_driver_method
from .queue import Queue
from .config import default as default_config
from .mesos_pb2_factory import build


class SatyrScheduler(Scheduler, Skeleton):
    ALLOWED_HANDLERS = ['resourceOffers', 'statusUpdate', 'frameworkMessage']

    task_stats = {'running': 0, 'successful': 0, 'failed': 0, 'created': 0}
    driver_states = {'is_starting': True, 'force_shutdown': False, 'is_running': True}

    def __init__(self, config, task_executor):
        print 'Starting framework [%s]' % config['name']
        self.config = dict(default_config, **config)
        self.task_executor = task_executor
        self.name = config['name']
        self.task_queue = Queue()
        self.satyr = None

    def add_job(self, message):
        self.task_queue.append(message)

    def should_be_running(self):
        return self.task_queue or self.task_stats['running'] >= self.config['max_tasks']

    def shutdown_if_done(self, driver):
        if self.driver_states['force_shutdown'] or not any((
                self.config.get('permanent'),
                self.driver_states['is_starting'],
                self.task_stats['running'],
                len(self.task_queue))):
            print 'We are finished.'
            self.shutdown(driver)

    def shutdown(self, driver):
        driver.stop()
        self.driver_states['is_running'] = False


def create_task_executor(config):
    executor = build('executor_info', config)
    uri = executor.command.uris.add()
    uri.value = os.path.join(config['executor_dir'], config['executor_file'])
    uri.extract = False

    return executor


def create_scheduler(config, executor_message_handler=None, job=None):
    scheduler = SatyrScheduler(config, create_task_executor(config))
    if executor_message_handler:
        scheduler.add_handler('frameworkMessage', executor_message_handler)
    scheduler.add_handler('resourceOffers', ResourceOfferHandler(scheduler))
    scheduler.add_handler('statusUpdate', StatusUpdateHandler(scheduler))

    if not job is None:
        scheduler.add_job(job)

    return scheduler


def run_scheduler(scheduler):
    driver = MesosSchedulerDriver(scheduler, build('framework_info', scheduler.config), scheduler.config['master'])
    framework_thread = Thread(target=create_driver_method(driver), args=())
    framework_thread.start()
    return framework_thread
