[![Build Status](http://drone.lensa.com:8000/api/badges/lensacom/satyr/status.svg)](http://drone.lensa.com:8000/lensacom/satyr)

![satyr](https://s3.amazonaws.com/lensa-rnd-misc/satyr2.png)

# An extensible Mesos library for Python
###### aka. the distributed snake-charmer


Satyr's intention is to simplify the process of writing python frameworks
for Mesos. Satyr provides multiple components and interfaces to cover various
levels of complexity needs.

## Notable Features

- Comfortable Pythonic interface instead of the C++ syntax
- Magical Protobuf wrapper to easily extend messages with custom functionality
- Multiple weighted Bin-Packing heuristics for optimized scheduling
- Easily extensibe QueueScheduler implementation
- Python multiprocessing.Pool interface

## Install

`pip install satyr` or use [lensa/satyr](https://hub.docker.com/r/lensa/satyr/) Docker image

Requirements:
- mesos.interface (installable via pip)
- mesos.native (binary .egg downloadable from mesosphere.io)

Configuration:
- `MESOS_MASTER=zk://127.0.0.1:2181/mesos`


## Examples

### Multiprocessing

This is the most simple use case. It's similar to python's
[multiprocessing interface](https://docs.python.org/2/library/multiprocessing.html)
but runs processes on a Mesos cluster (concurrently).

```python
from __future__ import print_function
from satyr.apis.multiprocessing import Pool


with Pool(name='satyr-pool') as pool:
    def mul(a, b):
        return a * b

    res1 = pool.apply_async(lambda a, b: a + b, [1, 2])
    res2 = pool.apply_async(mul, [2, 3])
    pool.wait()

    print(res1.get())
    print(res2.get())
```

### Work Queue Scheduler

Basic scheduler to submit various kind of workloads, eg.:
 - bash commands
 - docker executable containers
 - python callables
 - customized tasks (e.g. function executed via pypy)

```python
from __future__ import print_function
from satyr.scheduler import QueueScheduler, Running
from satyr.messages import PythonTask
from satyr.proxies.messages import Disk, Mem, Cpus


scheduler = QueueScheduler()
task = PythonTask(fn=sum, args=[range(10)], name='satyr-task',
                  resources=[Cpus(0.1), Mem(128), Disk(512)])

with Running(scheduler, name='satyr-scheduler'):
    res = scheduler.submit(task)  # return AsyncResult
    print(res.get(timeout=30))
```

### Custom Scheduler

You can make your own scheduler built on QueueScheduler or for more complex
needs there's a [Scheduler](satyr/interface.py) interface which you can use
to create one from scratch. (However in this case you'll have to implement
some of the functionalities already in [QueueScheduler](satyr/scheduler.py))

```python
from __future__ import print_function
from satyr.scheduler import QueueScheduler, Running
from satyr.messages import PythonTask
from satyr.proxies.messages import Disk, Mem, Cpus


class CustomScheduler(QueueScheduler):

    def on_update(self, driver, status):
        """You can hook on the events defined in the Scheduler interface.

        They're just more conveniantly named methods for the basic
        mesos.interface functions but this is how you can add some
        custom logic to your framework in an easy manner.
        """
        logging.info(
            "Status update received for task {}".format(status.task_id))
        super(CustomScheduler, self).on_update(driver, status)


scheduler = CustomScheduler()
task = PythonTask(fn=sum, args=[range(9)], name='satyr-task',
                  resources=[Cpus(0.1), Mem(128), Disk(512)])

with Running(scheduler, name='satyr-custom-scheduler'):
    res = scheduler.submit(task)
    print(res.get(timeout=60))
```

Also this way you can easily implement your own resource offer handling logic by
overriding the `on_offers(self, driver, offers)` method in which we give you a
helping hand with comparable Offers and TaskInfos (basic arithmetic operators
are also overloaded).

```python
from satyr.interface import Scheduler
from satyr.proxies.messages import Offer, TaskInfo


class CustomScheduler(Scheduler):
    ...
    def on_offers(self, driver, offers):
        ...
        task = self.get_next_task()
        for offer in offers
            if task < offer:
                task.slave_id = offer.slave_id
                driver.launch(offer, [task])
        # decline unused offers or launch with empty task list
        ...
```

## Optimized Task Placement

Satyr implements multiple weighted heuristics to solve the
[Bin-Packing Problem](https://en.wikipedia.org/wiki/Bin_packing_problem):

- First-Fit
- First-Fit-Decreasing
- Max-Rest
- Best-Fit
- Best-Fit-Decreasing

see [binpack.py](satyr/binpack.py).

The benefits of using bin-packing has been proven by
[Netflix/Fenzo](https://github.com/Netflix/Fenzo) in
[Heterogeneous Resource Scheduling Using Apache Mesos](http://events.linuxfoundation.org/sites/events/files/slides/Prezo-at-MesosCon2015-Final.pdf)

## Built in Task Types

### Command

The most basic task executes a simple command, Mesos will run CommandInfo's
value with `/bin/sh -c`. Also, if you want to run your task in a Docker
container you can provide some additional information for the task.

```python
from satyr.proxies.messages import TaskInfo, CommandInfo


task = TaskInfo(name='command-task', command=CommandInfo(value='echo 100'))
task.container.type = 'DOCKER'
task.container.docker.image = 'lensacom/satyr:latest'
```

### Python

[PythonTask](/satyr/messages.py) is capable of running arbitrary python code on
your cluster. It sends [cloudpickled](https://github.com/cloudpipe/cloudpickle)
methods and arguments to the matched mesos-slave for execution.
Note that python tasks run in [lensa/satyr](https://hub.docker.com/r/lensa/satyr/)
Docker container by default.

```python
from satyr.messages import PythonTask


# You can pass a function or a lambda in place of sum for fn.
task = PythonTask(name='python-task', fn=sum, args=[range(5)])
```

## Custom Task

Customs tasks can be written by extending [TaskInfo](/satyr/proxies/messages.py)
or any existing descendants.
If you're walking down the former path you'll most likely have to deal with
protobuf in your code; worry not, we have some magic wrappers for you to provide
customizable messages.

```python
from __future__ import print_function
from satyr.proxies.messages import TaskInfo
from mesos.interface import mesos_pb2


class CustomTask(TaskInfo):
    # descriptive protobuf template the wrapper matched against
    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='custom')]))

    @property
    def uppercase_task_name():
        return self.name.upper()

    def on_update(self, status):
         logging.info('Custom task has received a status update')

    def custom_method(self):
         print("Arbitrary stuff")
```

## One-Off Executor

This Executor implementation simply runs the received python function with the
provided arguments, then sends back the result in a reliable fashion.

```py
class OneOffExecutor(Executor):

    def on_launch(self, driver, task):
        def run_task():
            driver.update(task.status('TASK_RUNNING'))
            logging.info('Sent TASK_RUNNING status update')

            try:
                logging.info('Executing task...')
                result = task()
            except Exception as e:
                logging.exception('Task errored')
                driver.update(task.status('TASK_FAILED', message=e.message))
                logging.info('Sent TASK_RUNNING status update')
            else:
                driver.update(task.status('TASK_FINISHED', data=result))
                logging.info('Sent TASK_FINISHED status update')

        thread = threading.Thread(target=run_task)
        thread.start()
```

## Warning (at the end)

This is a pre-release!

- proper documentation
- python futures api
- more detailed examples
- and CONTRIBUTION guide
- dask.mesos backend

are coming!
