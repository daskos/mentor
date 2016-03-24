from __future__ import absolute_import, division, print_function

from threading import Thread

from mesos.interface import Scheduler, mesos_pb2
from mesos.native import MesosSchedulerDriver

from .driver import run
from .mesos_pb2_factory import build
from .queue import Queue


class SatyrScheduler(Scheduler):
    task_status_modifiers = {
        mesos_pb2.TASK_RUNNING: [('running', 1)],
        mesos_pb2.TASK_FINISHED: [('running', -1), ('successful', 1)],
        mesos_pb2.TASK_FAILED: [('running', -1), ('failed', 1)],
        mesos_pb2.TASK_LOST: [('running', -1), ('failed', 1)],
        mesos_pb2.TASK_KILLED: [('running', -1), ('failed', 1)],
        mesos_pb2.TASK_STAGING: [],
        mesos_pb2.TASK_STARTING: []
    }

    task_stats = {'running': 0, 'successful': 0, 'failed': 0, 'created': 0}
    driver_states = {'is_starting': True,
                     'force_shutdown': False,
                     'is_running': True}

    def __init__(self, config, framework_message):
        print('Starting framework [%s]' % config['name'])
        self.config = config
        self.framework_message = framework_message
        self.name = config['name']
        self.task_queue = Queue()
        self.satyr = None

    def frameworkMessage(self, driver, executorId, slaveId, data):
        self.framework_message(self, driver, executorId, slaveId, data)

    def statusUpdate(self, driver, taskStatus):
        status = taskStatus.state
        print('Recieved a status update [%s]' % status)
        if status not in self.task_status_modifiers:
            print('Unknown state code [%s]' % status)

        for name, value in self.task_status_modifiers[status]:
            self.task_stats[name] += value

        self.driver_states['is_starting'] = False

        # TODO do something w/ this extreme code smell
        if self.satyr:
            self.satyr.update_task_status(taskStatus)

    def resourceOffers(self, driver, offers):
        print('Recieved %d resource offer(s)' % len(offers))

        filters = build('filters', self.config)

        def handle_offers(driver, offers):
            self.shutdown_if_done(driver)
            for offer in offers:
                if not self.should_be_running():
                    print('Declining offer [%s]' % offer.id)
                    driver.declineOffer(offer.id, filters)
                    continue

                tasks = [create_task(offer, task) for task in create_task_list(
                    get_resources_from_offer(offer), [])]

                print('We\'re starting %d new task(s)' % len(tasks))
                driver.launchTasks(offer.id, tasks) if tasks else driver.declineOffer(
                    offer.id, filters)

        def get_resources_from_offer(offer):
            return {res.name: res.scalar.value for res in offer.resources}

        def create_task_list(resources, tasks):
            if not len(self.task_queue):
                return tasks

            task = self.task_queue.popleft()
            task_resources = create_task_resources(task)
            fits = task_fits_into_remaining_resources(
                resources, task_resources)

            if fits and len(tasks) < self.config['max_tasks']:
                tasks.append(task)
                return create_task_list(
                    create_new_task_resources(resources, task_resources), tasks)

            self.task_queue.appendleft(task)

            return tasks

        def task_fits_into_remaining_resources(resources, task_resources):
            """Checks if the following task fits into the remaining
            resources of the offer. Currently only this stupid
            implementation is available. It checks the tasks according
            to the list and only verifies if the current task fits.
            A smarter, resource optimized method could be easely
            introduced."""
            def fits(name, val):
                return val - task_resources.get(name, 0) > 0

            return all([fits(name, val) for name, val in resources.items() if name in task_resources])

        def create_new_task_resources(resources, task_resources):
            def calc(name, val):
                return val - task_resources.get(name, 0)

            return {name: calc(name, val) for name, val in resources.items() if name in task_resources}

        def create_task(offer, data):
            self.task_stats['created'] += 1

            executor = build('executor_info', self.config, data)
            task = build('task_info', data, self, executor, offer)
            add_resources_to_task(task, data)

            return task

        def add_resources_to_task(task, data):
            for name, val in create_task_resources(data).items():
                res = task.resources.add()
                res.name = name
                res.type = mesos_pb2.Value.SCALAR
                res.scalar.value = val

        def create_task_resources(data):
            if isinstance(data, dict) and data.get('resources'):
                return data['resources']

            return self.config['resources']

        t = Thread(target=handle_offers, args=(driver, offers))
        t.start()

    def add_job(self, message):
        self.task_queue.append(message)

    def should_be_running(self):
        return self.task_queue or self.task_stats['running'] >= self.config['max_tasks']

    def shutdown_if_done(self, driver):
        if self.driver_states['force_shutdown'] or not any((
                self.config['permanent'],
                self.driver_states['is_starting'],
                self.task_stats['running'],
                len(self.task_queue))):
            print('We are finished.')
            self.shutdown(driver)

    def shutdown(self, driver):
        driver.stop()
        self.driver_states['is_running'] = False

    def run(self):
        driver = MesosSchedulerDriver(self, build('framework_info', self.config), self.config['master'])
        framework_thread = Thread(target=run(driver), args=())
        framework_thread.start()
        return framework_thread
