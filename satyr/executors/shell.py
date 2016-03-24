import json
import os

from mesos.interface import mesos_pb2
from satyr.executor import SatyrExecutor


def shell_command_handler(scheduler, driver, task):
    scheduler.send_status_update(driver, task, mesos_pb2.TASK_RUNNING)

    cmd = json.loads(task.data)
    cmd = cmd.get('cmd', 'echo "No cmd in task."') if isinstance(
        cmd, dict) else cmd

    scheduler.send_framework_message(driver, 'Running command: %s' % cmd)
    os.system(cmd)
    scheduler.send_framework_message(driver, 'Done!')

    scheduler.send_status_update(driver, task, mesos_pb2.TASK_FINISHED)


if __name__ == '__main__':
    e = SatyrExecutor(shell_command_handler)
    e.run()
