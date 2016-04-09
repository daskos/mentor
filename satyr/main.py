from __future__ import absolute_import, division, print_function



from .scheduler import Scheduler
from .utils import catch, run_daemon


# from satyr import Framework

# class WorkQueueFramework(Framework):

#     def __init__(task_queue, result_queue):
#         self.tasks = task_queue
#         self.results = result_queue

#     def runnable_tasks(self):
#         return [self.tasks.get()]

#     def match(self, tasks, offers): # called on resource_offers
#         return BinPacker(tasks, offers)

#     def should_terminate(self): # called on status_update
#         return len(self.tasks) == 0

#     def on_update(task, update):
#         result = pickle.loads(update.data)
#         self.results.put((task.id, result))


# tasks = Queue()
# results = Queue()

# fw = WorkQueueFramework(name="pina", tasks, results)
# fw.run_scheduler()

# fw.run_executor()


# cmd = "..."

# def fn(queue):
#     queue.put("anyad-picsaja")

# first = Task(command=cmd, cpu=1, mem=128, image="python:2-alpine")  # command executor

# second = Task(callback=fn, args=[results], cpu=1, mem=128, image="python:2-alpine")  # pickled executor


# tasks.put(first)

from .proxies.messages import TaskInfo, encode, Filters

class Test(Scheduler):

    def match(self, offers):
        return {} # mappings

    def on_offers(self, driver, offers):
        #to_launch = self.match(offers)
        #to_decline = [o for o in offers if o not in to_launch]

        #print(offers[0].ports)

        task = TaskInfo(name='test', task_id={'value': 'test-id'}, resources=[
            {'name': 'cpu', 'scalar': {'value': 1.0}, 'type': 'SCALAR'},
            {'name': 'mem', 'scalar': {'value': 64}, 'type': 'SCALAR'}])

        for offer in offers:
            if offer > task:
                task.slave_id = offer.slave_id
                print(encode(offer.id))
                print(encode(task))
                print(encode(Filters()))
                driver.launch(offer.id, [task])
            else:
                driver.decline(offer.id)



if __name__ == '__main__':
    fw = Test(name='pinasen')
    run_daemon('Mesos Test Framework', fw)
