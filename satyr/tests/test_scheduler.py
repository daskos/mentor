class Test(Scheduler):

    def match(self, offers):
        return {} # mappings

    def on_offers(self, driver, offers):
        #print(driver)
        #print(offers)

        to_launch = self.match(offers)
        to_decline = [o for o in offers if o not in to_launch]

        for offer, tasks in to_launch.items():
            driver.launch(offer, tasks, filters=None)  # filters?

        for offer in to_decline:  # decline remaining unused offers
            driver.decline(offer)



import os
from mesos.interface import mesos_pb2
from satyr.config import Config
from satyr.executor import SatyrExecutor
from satyr.scheduler import SatyrScheduler

config = Config(conf={
    'id': 'satyr',
    'name': 'Satyr',
    'resources': {'cpus': 0.1, 'mem': 128},
    'max_tasks': 10,
    'master': '192.168.1.80:5050',
    'user': 'nagyz',
    'filter_refuse_seconds': 10,
    'permanent': False,
    'command': 'python %s/example.py' % os.path.dirname(os.path.realpath(__file__))
})






def run_on_scheduler(scheduler, driver, executorId, slaveId, data):
    print data


def run_on_executor(executor, driver, task):
    executor.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)
    executor.send_framework_message(driver, 'Sleep!')
    print 'sleeping...'
    time.sleep(3)
    executor.send_framework_message(driver, 'Wake up!')
    executor.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)


def test_run():
    s = SatyrScheduler(config, run_on_scheduler)
    s.add_job({'cmd': 'echo 1'})
    s.run()

    # # With name it runs the scheduler otherwise the executor.
    # if len(sys.argv) == 1:
    #     e = SatyrExecutor(run_on_executor)
    #     e.run()
    # else:
