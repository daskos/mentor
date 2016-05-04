[![Build Status](http://52.0.47.203:8000/api/badges/lensacom/satyr/status.svg)](http://52.0.47.203:8000/lensacom/satyr)

# Satyr

![Satyr](http://uploads3.wikiart.org/images/jacob-jordaens/bust-of-satyr-1621.jpg!Blog.jpg)

A python Mesos framework library. Satyr's intention is to simplify the process of writing frameworks for Mesos. It gives multiple interfaces and each of them covers various levels of complexity needs.

## Examples

### Multiprocessing

This is the most simple use case. It's similar to python's own [multiprocessing interface](https://docs.python.org/2/library/multiprocessing.html) but can run your processes concurrently on a Mesos cluster.

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

### QueueScheduler

The multiprocessing interface basicly hides the QueueScheduler but it can be useful to submit more fine grained tasks (For example your processes need more resources than the defaults.)

```python
from __future__ import print_function
from satyr.scheduler import QueueScheduler, Running
from satyr.messages import PythonTask
from satyr.proxies.messages import Disk, Mem, Cpus


scheduler = QueueScheduler()
task = PythonTask(fn=sum, args=[range(10)], name='satyr-task',
                  resources=[Cpus(0.1), Mem(128), Disk(512)])

with Running(scheduler, name='satyr-scheduler'):
    res = scheduler.submit(task)
    res.wait()
    print(res.get())
```

### Custom scheduler

You can make your own scheduler built on QueueScheduler or for more complex needs there's a [Scheduler](satyr/interface.py) interface which you can use to create one from scratch. (However in this case you'll have to implement some of the functionalities already in [QueueScheduler](satyr/scheduler.py))

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
        custom logic to your framework in an easy manner."""
        super(CustomScheduler, self).on_update(driver, status)
        print(status.state)

scheduler = CustomScheduler()
task = PythonTask(fn=sum, args=[range(9)], name='satyr-task',
                  resources=[Cpus(0.1), Mem(128), Disk(512)])

with Running(scheduler, name='satyr-custom-scheduler'):
    res = scheduler.submit(task)
    res.wait()
    print(res.get())
```

Also this way you can easily implement your own resource offer handling logic by overriding the `on_offers(self, driver, offers)` method in which we give you a helping hand with comparable Offers and TaskInfos. (Comparison is based on provided and required resources.)

```python
from satyr.interface import Scheduler
from satyr.proxies.messages import Offer, TaskInfo


class CustomScheduler(Scheduler):
    ...
    def on_offers(self, driver, offers):
        ...
        # We're pretty sure you'll not be doing anything like this.
        offer = Offer(resources=[Cpus(2), Mem(512)])
        task = TaskInfo(resources=[Cpus(0.5), Mem(128)])
        offer > task  # True
        ...
```

Currently we only have some basic resource handling but we're up to solve this issue with some nice Bin-Packing heuristics (First-Fit(-Decreasing), Max-Rest, Best-Fit(-Decreasing)).

### Built in task types

#### Command

The most basic task executes a simple command, Mesos will run CommandInfo's value with `/bin/sh -c`. Also, if you want to run your task in a Docker container you can provide some additional information for the task.

```python
from satyr.proxies.messages import TaskInfo, CommandInfo


task = TaskInfo(name='command-task', command=CommandInfo(value='echo 100'))
task.container.type = 'DOCKER'
task.container.docker.image = 'lensacom/satyr:latest'
```

#### Python

As it's name says a [PythonTask](/satyr/messages.py) is capable of running some python code on your cluster. It sends pickled methods to the executor which then will run it. (In fact it wraps the base TaskInfo.) Note that python tasks will run in Docker containers by default.

```python
from satyr.messages import PythonTask


# You can pass a function or a lambda in place of sum for fn.
task = PythonTask(name='python-task',
                  fn=sum, args=[range(5)])
```

### Custom task

Customs tasks can be written by extending [TaskInfo](/satyr/proxies/messages.py) or any existing tasks. If you're walking down the former path you'll most likely have to deal with protobuf in your code; worry not, we have some magic wrappers for you to provide easely extensible messages. (**TODO** Clear this up.)

```python
from __future__ import print_function
from satyr.proxies.messages import TaskInfo
from mesos.interface import mesos_pb2


class CustomTask(TaskInfo):
    proto = mesos_pb2.TaskInfo(
        labels=mesos_pb2.Labels(
            labels=[mesos_pb2.Label(key='custom')]))

    def on_update(self, status):
         logging.info('Custom task has received a status update')

    def custom_method(self):
         print("Arbitrary stuff")
```

### Custom executor

**TODO**

## Configuration

There's only a handful of configurations need to be set outside of code to get Satyr running. Each of them can be set as an environment variable.

* MESOS_MASTER=zk://127.0.0.1:2181/mesos
* ZOOKEEPER_HOST=127.0.0.1:2181
