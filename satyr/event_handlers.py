from mesos.interface import mesos_pb2
from math import floor
import threading

fltr = mesos_pb2.Filters()
fltr.refuse_seconds = 300


def resource_offer_handler(self, driver, offers):
    print 'Recieved %d resource offer(s)' % len(offers)

    def get_resources_from_offer(offer):
        return {res.name: res.scalar.value for res in offer.resources}

    def add_resource(task, name, value):
        res = task.resources.add()
        res.name = name
        res.type = mesos_pb2.Value.SCALAR
        res.scalar.value = value

    def create_task_resources(data):
        if isinstance(data, dict) and data.get('resources'):
            return data['resources']

        return self.config['resources']

    def create_task(offer, data):
        self.task_stats['created'] += 1

        task = mesos_pb2.TaskInfo()
        task.task_id.value = str(self.task_stats['created']).zfill(5)
        task.slave_id.value = offer.slave_id.value
        task.name = '%s %s' % (self.name, task.task_id.value)
        task.executor.MergeFrom(self.task_executor)
        task.data = data.get('msg', '') if isinstance(data, dict) else data

        for name, val in create_task_resources(data).items():
            add_resource(task, name, val)

        return task

    def task_fits_into_remaining_resources(resources, task_resources):
        return all([val - task_resources.get(name, 0) > 0 for name, val in resources.items() if name in task_resources])

    def create_new_task_resources(resources, task_resources):
        return {name: val - task_resources.get(name, 0) for name, val in resources.items() if name in task_resources}

    def create_task_list(resources, tasks):
        if not len(self.task_queue):
            return tasks

        task = self.task_queue.popleft()
        task_resources = create_task_resources(task)
        if task_fits_into_remaining_resources(resources, task_resources) and len(tasks) < self.config['max_tasks']:
            tasks.append(task)
            return create_task_list(create_new_task_resources(resources, task_resources), tasks)

        self.task_queue.appendleft(task)

        return tasks

    def handle_offers():
        self.shutdown_if_done(driver)
        for offer in offers:
            if not self.task_queue or self.task_stats['running'] >= self.config['max_tasks']:
                print 'Declining offer [%s]' % offer.id
                driver.declineOffer(offer.id, fltr)
                continue

            tasks = [create_task(offer, task) for task in create_task_list(get_resources_from_offer(offer), [])]

            print 'We\'re starting %d new task(s)' % len(tasks)
            driver.launchTasks(offer.id, tasks) if tasks else driver.declineOffer(offer.id, fltr)

    t = threading.Thread(target=handle_offers)
    t.start()


def status_update_handler(self, driver, taskStatus):
    status = taskStatus.state
    print 'Recieved a status update [%s]' % status

    if status == mesos_pb2.TASK_RUNNING: # 1
        self.task_stats['running'] += 1
    elif status == mesos_pb2.TASK_FINISHED: # 2
        self.task_stats['running'] -= 1
        self.task_stats['successful'] += 1
    elif status in [mesos_pb2.TASK_FAILED, mesos_pb2.TASK_LOST, mesos_pb2.TASK_KILLED]: # 3, 5, 4
        self.task_stats['running'] -= 1
        self.task_stats['failed'] += 1
    elif status in [mesos_pb2.TASK_STAGING, mesos_pb2.TASK_STARTING]: # 6, 0
        return
    else:
        print 'Unknown state code [%s]' % status

    self.driver_states['is_starting'] = False
