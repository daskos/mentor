import json
import os

from mesos.interface import mesos_pb2
from satyr import executor


def create_shell_executor():
    def shell_command_handler(self, driver, task):
        self.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)

        cmd = json.loads(task.data)
        cmd = cmd.get('cmd', 'echo "No cmd in task."') if isinstance(
            cmd, dict) else cmd

        self.send_framework_message(driver, 'Running command: %s' % cmd)
        os.system(cmd)
        self.send_framework_message(driver, 'Done!')

        self.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)

    return executor.create_executor(shell_command_handler)


if __name__ == '__main__':
    shell_cmd = create_shell_executor()
    executor.run_executor(shell_cmd)
