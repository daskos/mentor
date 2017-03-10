import operator
import copy
import six
import cloudpickle
from .utils import remote_exception
import logging
from uuid import uuid4
from mentos.utils import decode_data,encode_data
from functools import wraps
from six import iteritems,iterkeys,get_function_code

log = logging.getLogger(__name__)

logging.getLogger().setLevel(logging.DEBUG)


def decode_message(x):
    """ Recursively transforms a dictionary into a Message via copy.

    """
    if isinstance(x, dict):
        return Message((k, decode_message(v)) for k, v in iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(decode_message(v) for v in x)
    else:
        return x


class Message(dict):
    """ A dictionary that provides attribute-style access.
    """
    @classmethod
    def convert(cls,x):
        if isinstance(x, dict):
            return cls((k, cls.convert(v)) for k, v in iteritems(x))
        elif isinstance(x, (list, tuple)):
            return type(x)(cls.convert(v) for v in x)
        else:
            return x


    def __contains__(self, k):
        """
        """
        try:
            return dict.__contains__(self, k) or hasattr(self, k)
        except:
            return False

    # only called if k not found in normal places
    def __getattr__(self, k):
        """ Gets key if it exists, otherwise throws AttributeError.
        """
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        """
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        """ Deletes attribute k if it exists, otherwise deletes key k. A KeyError
            raised by deleting the key--such as when the key is missing--will
            propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)


    def __repr__(self):
        """ Invertible* string-form of a Message.
        """
        keys = list(iterkeys(self))
        keys.sort()
        args = ', '.join(['%s=%r' % (key, self[key]) for key in keys])
        return '%s(%s)' % (self.__class__.__name__, args)

    def __dir__(self):
        return self.keys()

    @staticmethod
    def fromDict(d):
        return decode_message(d)

def Cpus(value):
    return Message({'name': 'cpus', 'role': '*', 'scalar': Message({'value':value}), 'type': 'SCALAR'})

def Mem(value):
    return Message({'name': 'mem', 'role': '*', 'scalar':  Message({'value':value}), 'type': 'SCALAR'})

def Disk(value):
    return Message({'name': 'disk', 'role': '*', 'scalar': Message({'value':value}), 'type': 'SCALAR'})

def Ports(begin,end):
    return Message({'name': 'disk', 'role': '*', 'ranges': Message({'range':[Message({'begin': begin, 'end': end})]}), 'type': 'SCALAR'})


class ResourceMixin(object):

    zeroes = {'cpus': 0.0, 'mem': 0.0, 'disk': 0.0, 'ports': [{"begin":0.0,"end":0.0}]} # gpu

    @staticmethod
    def flatten(message):
        flattened = {}
        if  isinstance(message, (int, float, complex)):
            val = message
            message = {"resources":[Cpus(val),Disk(val),Mem(val)]}
        for r in message["resources"]:
            if r["type"]=="RANGES":
                flattened[r['name']] = r['ranges']['range']
            else:
                flattened[r['name']] = r['scalar']['value']
        return flattened

    def apply(self, op, other):
        a = self.flatten(self)
        b = self.flatten(other)
        out = {}
        for k, v in self.zeroes.items():
            if k=="ports":
                a = set([ (e["begin"],e["end"]) for e in a.get(k, v)])
                b = set([ (e["begin"],e["end"]) for e in b.get(k, v)])
                if op==operator.add:
                    out[k] = a.union(b)
                elif op==operator.sub:
                    out[k] = a.difference(b)
            else:
                out[k] = op(a.get(k, v), b.get(k, v))
        return out

    def __eq__(self, other):
        return all(self.apply(operator.eq, other).values())

    def __ne__(self, other):
        return all(self.apply(operator.ne, other).values())

    def __lt__(self, other):
        return all(self.apply(operator.lt, other).values())

    def __le__(self, other):
        return all(self.apply(operator.le, other).values())

    def __gt__(self, other):
        return any(self.apply(operator.gt, other).values())

    def __ge__(self, other):
        return any(self.apply(operator.ge, other).values())

    def update(self,resource_update):
        message = copy.deepcopy(self)
        for r in message['resources']:
            if r["type"] == "RANGES":
               if r["name"] in resource_update:
                  r["ranges"]["range"]  = [{"begin":a,"end":b} for a,b in resource_update[r["name"]]]
            else:
                if r["name"] in resource_update:
                    r["scalar"]["value"] = resource_update[r["name"]]

        return message

    def __add__(self, second):
        return self.update(self.apply(operator.add,second))

    def __sub__(self, second):
        return self.update(self.apply(operator.sub, second))

    def __radd__(self, second):  # to support sum()
        if second ==0:
           second = self.__class__(resources=[Cpus(0), Mem(0), Disk(0)])
        return self + second

    def __iadd__(self, second):
        added = self + second
        self["resources"] = added["resources"]
        return self

    def __isub__(self, second):
        subbed = self - second
        self["resources"] = subbed["resources"]
        return self

    @property
    def cpus(self):
        for res in self.resources:
            if res["name"] == "cpus":
                return Message.convert(res)
        return Cpus(0.0)

    @property
    def mem(self):
        for res in self["resources"]:
            if res["name"] == "mem":
                return Message.convert(res)
        return Mem(0.0)

    @property
    def disk(self):
        for res in self["resources"]:
            if res["name"] == "disk":
                return Message.convert(res)
        return Disk(0.0)

    @property
    def ports(self):
        for res in self["resources"]:
            if res["name"]=="ports":
                return [(rng["begin"], rng["end"]) for rng in res["ranges"]["range"]]
        return Ports(0,0)


class TaskInfo(ResourceMixin, Message):
    @staticmethod
    def fromDict(d):
        return TaskInfo(**decode_message(d))



class Offer(ResourceMixin, Message):
    @property
    def slave_id(self):
        try:
            return self["slave_id"]
        except KeyError:
            return self["agent_id"]

    @property
    def agent_id(self):
        try:
            return self["agent_id"]
        except KeyError:
            return self["slave_id"]

    @staticmethod
    def fromDict(d):
        return Offer(**decode_message(d))


class TaskStatus(Message):

    def is_staging(self):
        return self.state == 'TASK_STAGING'

    def is_starting(self):
        return self.state == 'TASK_STARTING'

    def is_running(self):
        return self.state == 'TASK_RUNNING'

    def has_finished(self):
        return self.state == 'TASK_FINISHED'

    def has_succeeded(self):
        return self.state == 'TASK_FINISHED'

    def has_killed(self):
        return self.state == 'TASK_KILLED'

    def has_failed(self):
        return self.state in ['TASK_FAILED', 'TASK_LOST', 'TASK_KILLED',
                              'TASK_ERROR']

    def has_terminated(self):
        return self.has_succeeded() or self.has_failed()


class PythonTaskStatus(TaskStatus):

    def __init__(self, data=None, **kwargs):

        self.labels = Message(labels=[Message(key='python')])
        self.data = encode_data(cloudpickle.dumps(kwargs.get("data",None)))

        super(PythonTaskStatus, self).__init__(**kwargs)

    @property
    def result(self):
        return cloudpickle.loads(decode_data(self["data"]))

    @property
    def exception(self):
        try:
            return remote_exception(*self.result)
        except:
            return None

    @staticmethod
    def fromDict(d):
        return PythonTaskStatus(**decode_message(d))

# TODO create custom messages per executor
class PythonTask(TaskInfo):

    def __init__(self, fn=None, args=[], kwargs={},
                 resources=[Cpus(0.1), Mem(128), Disk(0)],
                 executor=None, retries=3, **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.task_id  = self.get("task_id",  Message(value=str(uuid4())))
        self.status = PythonTaskStatus(task_id=self.task_id, state='TASK_STAGING')
        self.executor = executor or PythonExecutor("python-executor")
        self.data = encode_data(cloudpickle.dumps(self.get("data",(fn, args, kwargs))))
        self.resources = resources
        self.retries = retries
        self.attempt = 1
        self.labels = Message(labels=[Message(key='python')])

    def __call__(self):
        fn, args, kwargs = cloudpickle.loads(decode_data(self.data))
        return fn(*args, **kwargs)

    def update(self, status):
        self.on_update(status)
        if status.has_succeeded():
            self.on_success(status)
        elif status.has_failed():
            self.on_fail(status)

    def on_update(self, status):
        self.status = status  # update task's status
        log.info('Task {} has been updated with state {}'.format(
            self.task_id.value, status.state))

    def on_success(self, status):
        log.info('Task {} has been succeded'.format(self.task_id.value))

    def on_fail(self, status):
        log.error('Task {} has been failed with state {} due to {}'.format(
            self.task_id.value, status.state, status.message))


class PythonExecutor(Message):

    def __init__(self, id, docker='satyr', force_pull=False,
                 envs={}, uris=[], **kwds):
        super(PythonExecutor, self).__init__(**kwds)
        self.container = Message(
            type='DOCKER',
            mesos=Message(
                image=Message(type='DOCKER',
                            docker=Message(name=docker))))
        self.executor_id = Message(value=id)
        self.command = Message(value='python -m satyr.executor',
                                   shell=True)
        self.force_pull = force_pull
        self.docker = docker
        self.envs = envs
        self.uris = uris

        self.labels = Message(labels=[Message(key='python')])

    @property
    def docker(self):
        return self.container.mesos.image.docker.name

    @docker.setter
    def docker(self, value):
        self.container.mesos.image.docker.name = value

    @property
    def force_pull(self):
        # cached is the opposite of force pull image
        return not self.container.mesos.image.cached

    @force_pull.setter
    def force_pull(self, value):
        self.container.mesos.image.cached = not value

    @property
    def uris(self):
        return [uri.value for uri in self.command.uris]

    @uris.setter
    def uris(self, value):
        self.command.uris = [{'value': v} for v in value]

    @property
    def envs(self):
        envs = self.command.environment.variables
        return {env.name: env.value for env in envs}

    @envs.setter
    def envs(self, value):
        envs = [{'name': k, 'value': v} for k, v in value.items()]
        self.command.environment = Message(variables=envs)


def transform(repeat=False,**trigger):
    def decorator(func):
        names = getattr(func,'_names',None)
        if names is None:
            code = get_function_code(func)
            names = code.co_varnames[:code.co_argcount]
        @wraps(func)
        def decorated(*args,**kwargs):
            all_args = kwargs.copy()
            for n,v in zip(names,args):
                all_args[n] = v
            for k,v in trigger.items():
                if k in all_args:
                    if repeat:
                        all_args[k] = [v.fromDict(arg) for arg in all_args[k]]
                    else:
                        all_args[k] = v.fromDict(all_args[k])
            return func(**all_args)
        decorated._names = names
        return decorated
    return decorator