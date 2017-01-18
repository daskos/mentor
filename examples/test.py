
from satyr.scheduler import Framework
from mentos.scheduler import SchedulerDriver
import os
import getpass
from satyr.messages.base import TaskID, Disk, Cpus, Mem, TaskInfo, CommandInfo, Environment

sched = Framework()
driver = SchedulerDriver(sched, "Queue", getpass.getuser())

driver.start()

from satyr.messages.satyr import PythonTask
import sys
executor = {
    "executor_id": {
        "value": "MinimalExecutor"
    },
    "name": "MinimalExecutor",
    "command": {
        "value": '%s %s' % (
            sys.executable, "~/workdir/mesos/malefico/malefico/executor.py"
        )

    }

}


task  = TaskInfo(name='command-task', command=CommandInfo(value='echo $HOME'), resources=[Cpus(0.1), Mem(128), Disk(0)])
# task = PythonTask(task_id=TaskID(value='test-task-id'), executor=executor,
#                   fn=sum, args=[range(5)],
#                   resources=[Cpus(0.1), Mem(128), Disk(0)])
sched.submit(task)
sched.wait()
print("Clean Exit, I guess")
