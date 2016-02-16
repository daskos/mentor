from mesos.interface import mesos_pb2
import threading

from ..mesos_pb2_factory import build


class ResourceOfferHandler(object):
    """Handles resource offer calls and creates new
    tasks to run on the Mesos cluster."""

    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.filters = build('filters', self.scheduler.config)

    def __call__(self, scheduler, driver, offers):
        """An offer should not block the scheduler so we try to
        run to run it separately from it. In the meantime more
        offers may arrive."""
        print 'Recieved %d resource offer(s)' % len(offers)
        t = threading.Thread(target=self.handle_offers, args=(driver, offers))
        t.start()

    def handle_offers(self, driver, offers):
        self.scheduler.shutdown_if_done(driver)
        for offer in offers:
            if not self.scheduler.should_be_running():
                print 'Declining offer [%s]' % offer.id
                driver.declineOffer(offer.id, self.filters)
                continue

            tasks = [self.create_task(offer, task) for task in self.create_task_list(self.get_resources_from_offer(offer), [])]

            print 'We\'re starting %d new task(s)' % len(tasks)
            driver.launchTasks(offer.id, tasks) if tasks else driver.declineOffer(offer.id, self.filters)

    def get_resources_from_offer(self, offer):
        return {res.name: res.scalar.value for res in offer.resources}

    def create_task_list(self, resources, tasks):
        if not len(self.scheduler.task_queue): return tasks

        task = self.scheduler.task_queue.popleft()
        task_resources = self.create_task_resources(task)
        if self.task_fits_into_remaining_resources(resources, task_resources) and len(tasks) < self.scheduler.config['max_tasks']:
            tasks.append(task)
            return self.create_task_list(self.create_new_task_resources(resources, task_resources), tasks)

        self.task_queue.appendleft(task)

        return tasks

    def task_fits_into_remaining_resources(iself, resources, task_resources):
        """Checks if the following task fits into the remaining
        resources of the offer. Currently only this stupid
        implementation is available. It checks the tasks according
        to the list and only verifies if the current task fits.
        A smarter, resource optimized method could be easely
        introduced."""
        return all([val - task_resources.get(name, 0) > 0 for name, val in resources.items() if name in task_resources])

    def create_new_task_resources(self, resources, task_resources):
        return {name: val - task_resources.get(name, 0) for name, val in resources.items() if name in task_resources}

    def create_task(self, offer, data):
        self.scheduler.task_stats['created'] += 1
        task = build('task_info', data, self.scheduler, offer)
        self.add_resources_to_task(task, data)

        return task

    def add_resources_to_task(self, task, data):
        for name, val in self.create_task_resources(data).items():
            res = task.resources.add()
            res.name = name
            res.type = mesos_pb2.Value.SCALAR
            res.scalar.value = val

    def create_task_resources(self, data):
        if isinstance(data, dict) and data.get('resources'):
            return data['resources']

        return self.scheduler.config['resources']
