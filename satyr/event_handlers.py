from mesos.interface import mesos_pb2
from math import floor
import threading

fltr = mesos_pb2.Filters()
fltr.refuse_seconds = 300


def resource_offer_handler(self, driver, offers):
    print 'Recieved %d resource offers' % len(offers)

    def get_resources_from_offer(offer):
        return {res.name: res.scalar.value for res in offer.resources}

    def calculate_available_places(resources):
        divide = lambda name, val: floor(val / self.config['resources'][name])
        results = [divide(name, val) for name, val in resources.iteritems() if name in self.config['resources']]
        return min(results)

    def add_resource(task, name, value):
        res = task.resources.add()
        res.name = name
        res.type = mesos_pb2.Value.SCALAR
        res.scalar.value = value

    def create_task(offer, data):
        self.task_stats['created'] += 1

        task = mesos_pb2.TaskInfo()
        task.task_id.value = str(self.task_stats['created']).zfill(5)
        task.slave_id.value = offer.slave_id.value
        task.name = '%s %s' % (self.name, task.task_id.value)
        task.executor.MergeFrom(self.task_executor)
        task.data = data

        for name, val in self.config['resources'].iteritems():
            add_resource(task, name, val)

        return task

    def handle_offers():
        self.shutdown_if_done(driver)
        for offer in offers:
            if not self.task_queue or self.task_stats['running'] >= self.config['max_tasks']:
                print 'Declining offer [%s]' % offer.id
                driver.declineOffer(offer.id, fltr)
                continue

            resources = get_resources_from_offer(offer)
            places = calculate_available_places(resources)

            tasks = []
            while self.task_queue and min(self.config['max_tasks'] - self.task_stats['running'], places) > 0:
                tasks.append(create_task(offer, self.task_queue.popleft()))
                places -= 1

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
