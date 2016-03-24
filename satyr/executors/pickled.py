import cloudpickle
from mesos.interface import mesos_pb2
from satyr.executor import SatyrExecutor


def pickled_function_handler(self, driver, task):
    self.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)

    job = cloudpickle.loads(task.data)
    result = job['func'](*job['args'], **job['kwargs'])
    response = {'msg': result, 'id': task.task_id.value, 'response': True}
    self.send_framework_message(driver, cloudpickle.dumps(response))

    self.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)


if __name__ == '__main__':
    e = SatyrExecutor(pickled_function_handler)
    e.run()
