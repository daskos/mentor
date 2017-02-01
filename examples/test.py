
from mentor.scheduler import Framework
from mentos.scheduler import SchedulerDriver
import os
import getpass
from mentor.messages.base import TaskID, Disk, Cpus, Mem, TaskInfo, CommandInfo, Environment

sched = Framework()
driver = SchedulerDriver(sched, "Queue", getpass.getuser())

driver.start()

from mentor.messages.satyr import PythonTask
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


task_infos = [{'task_id': {'value': '39e762f5-9767-4d7d-b187-67029df5b151'}, 'agent_id': {'value': '7037ef03-cbef-4e11-aac6-d662a5ef4179-S1'}, 'name': 'task 39e762f5-9767-4d7d-b187-67029df5b151', 'executor': {'executor_id': {'value': 'MinimalExecutor'}, 'name': 'MinimalExecutor', 'command': {'value': '/opt/anaconda3/envs/mentos/bin/python /home/arti/workdir/mesos/dmentos/examples/executor.py'}, 'resources': [{'name': 'mem', 'type': 'SCALAR', 'scalar': {'value': 32}}, {'name': 'cpus', 'type': 'SCALAR', 'scalar': {'value': 0.1}}]}, 'data': 'SGVsbG8gZnJvbSB0YXNrIDM5ZTc2MmY1LTk3NjctNGQ3ZC1iMTg3LTY3MDI5ZGY1YjE1MSE=', 'resources': [{'name': 'cpus', 'type': 'SCALAR', 'scalar': {'value': 0.2}}, {'name': 'mem', 'type': 'SCALAR', 'scalar': {'value': 128}}]}]
offers = [{'agent_id': {'value': '7037ef03-cbef-4e11-aac6-d662a5ef4179-S0'}, 'framework_id': {'value': '4dca24e0-63bf-4505-8023-f544de0842d6-0001'}, 'hostname': 'malefico.io', 'id': {'value': '4dca24e0-63bf-4505-8023-f544de0842d6-O2'}, 'resources': [{'name': 'ports', 'ranges': {'range': [{'begin': 1025, 'end': 60000}]}, 'role': '*', 'type': 'RANGES'}, {'name': 'cpus', 'role': '*', 'scalar': {'value': 7.9}, 'type': 'SCALAR'}, {'name': 'mem', 'role': '*', 'scalar': {'value': 14895.0}, 'type': 'SCALAR'}, {'name': 'disk', 'role': '*', 'scalar': {'value': 145941.0}, 'type': 'SCALAR'}], 'url': {'address': {'hostname': 'malefico.io', 'ip': '127.0.0.1', 'port': 5051}, 'path': '/slave(1)', 'scheme': 'http'}}, {'agent_id': {'value': '7037ef03-cbef-4e11-aac6-d662a5ef4179-S1'}, 'attributes': [{'name': 'mentos', 'text': {'value': 'true'}, 'type': 'TEXT'}], 'framework_id': {'value': '4dca24e0-63bf-4505-8023-f544de0842d6-0001'}, 'hostname': 'malefico.io', 'id': {'value': '4dca24e0-63bf-4505-8023-f544de0842d6-O3'}, 'resources': [{'name': 'cpus', 'role': '*', 'scalar': {'value': 0.5}, 'type': 'SCALAR'}, {'name': 'mem', 'role': '*', 'scalar': {'value': 1024.0}, 'type': 'SCALAR'}, {'name': 'ports', 'ranges': {'range': [{'begin': 11000, 'end': 11999}]}, 'role': '*', 'type': 'RANGES'}, {'name': 'disk', 'role': '*', 'scalar': {'value': 5114.0}, 'type': 'SCALAR'}], 'url': {'address': {'hostname': 'malefico.io', 'ip': '127.0.0.1', 'port': 5052}, 'path': '/slave(1)', 'scheme': 'http'}}]

