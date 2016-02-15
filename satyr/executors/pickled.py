from mesos.interface import mesos_pb2
from satyr import executor
import json, cloudpickle


def create_pickled_executor():
    def pickled_function_handler(self, driver, task):
        self.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)

        job = cloudpickle.loads(task.data)
        result = job['func'](*job['args'], **job['kwargs'])
        response = {'msg': result, 'id': task.task_id.value, 'response': True}
        self.send_framework_message(driver, cloudpickle.dumps(response))

        self.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)

    return executor.create_executor(pickled_function_handler)


if __name__ == '__main__':
    pickled_executor = create_pickled_executor()
    executor.run_executor(pickled_executor)
