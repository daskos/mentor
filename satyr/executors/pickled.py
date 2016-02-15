from mesos.interface import mesos_pb2
from satyr import executor
import json, cloudpickle


def create_pickled_executor():
    def pickled_function_handler(self, driver, task):
        self.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)

        func = cloudpickle.loads(task.data)

        self.send_framework_message(driver, 'Running pickled function.')
        func()
        self.send_framework_message(driver, 'Done!')

        self.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)

    return executor.create_executor(pickled_function_handler)


if __name__ == '__main__':
    pickled_executor = create_pickled_executor()
    executor.run_executor(pickled_executor)
