from satyr import Framework

class WorkQueueFramework(Framework):

    def __init__(task_queue, result_queue):
        self.tasks = task_queue
        self.results = result_queue

    def runnable_tasks(self):
        return [self.tasks.get()]

    def match(self, tasks, offers): # called on resource_offers
        return BinPacker(tasks, offers)

    def should_terminate(self): # called on status_update
        return len(self.tasks) == 0

    def on_update(task, update):
        result = pickle.loads(update.data)
        self.results.put((task.id, result))


tasks = Queue()
results = Queue()

fw = WorkQueueFramework(name="pina", tasks, results)
fw.run_scheduler()

fw.run_executor()


cmd = "..."

def fn(queue):
    queue.put("anyad-picsaja")

first = Task(command=cmd, cpu=1, mem=128, image="python:2-alpine")  # command executor

second = Task(callback=fn, args=[results], cpu=1, mem=128, image="python:2-alpine")  # pickled executor


tasks.put(first)
