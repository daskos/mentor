[![Build Status](http://52.0.47.203:8000/api/badges/lensacom/satyr/status.svg)](http://52.0.47.203:8000/lensacom/satyr)

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

### Built in task types

**TODO**

* command
* python

### Custom executor

**TODO**

## Configuration

**TODO**

Most of the configuration can be set in environment variables like:

* MESOS_MASTER=zk://127.0.0.1:2181/mesos
* ZOOKEEPER_HOST=127.0.0.1:2181

**TODO**
