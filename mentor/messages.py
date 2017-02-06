import operator
import copy
import six
import cloudpickle
from .utils import remote_exception
import logging
log = logging.getLogger(__name__)


# u('string') replaces the forwards-incompatible u'string'
if six.PY3:
    def u(string):
        return string
else:
    import codecs

    def u(string):
        return codecs.unicode_escape_decode(string)[0]

# dict.iteritems(), dict.iterkeys() is also incompatible
if six.PY3:
    iteritems = dict.items
    iterkeys = dict.keys
else:
    iteritems = dict.iteritems
    iterkeys = dict.iterkeys

class Message(dict):
    """ A dictionary that provides attribute-style access.
    """

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
        for r in message['resources']:
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
                return res
        return Cpus(0.0)

    @property
    def mem(self):
        for res in self["resources"]:
            if res["name"] == "mem":
                return res
        return Mem(0.0)

    @property
    def disk(self):
        for res in self["resources"]:
            if res["name"] == "disk":
                return res
        return Disk(0.0)

    @property
    def ports(self):
        for res in self["resources"]:
            if res["name"]=="ports":
                return [(rng["begin"], rng["end"]) for rng in res["ranges"]["range"]]
        return Ports(0,0)


class TaskInfo(ResourceMixin, Message):
    pass

class Offer(ResourceMixin, Message):
    pass



class PickleMixin(object):

    @property
    def data(self):
        return cloudpickle.loads(self['data'])

    @data.setter
    def data(self, value):
        self['data'] = cloudpickle.dumps(value)


class PythonTaskStatus(PickleMixin, Message):

    def __init__(self, data=None, **kwargs):
        super(PythonTaskStatus, self).__init__(**kwargs)
        self.labels = Message(labels=Message(key='python'))
        self.data = data

    @property
    def exception(self):
        try:
            return remote_exception(*self.data)
        except:
            return None


# TODO create custom messages per executor
class PythonTask(PickleMixin, TaskInfo):

     
    def __init__(self, fn=None, args=[], kwargs={},
                 resources=[Cpus(0.1), Mem(128), Disk(0)],
                 executor=None, retries=3, **kwds):
        super(PythonTask, self).__init__(**kwds)
        self.status = PythonTaskStatus(task_id=self.id, state='TASK_STAGING')
        self.executor = executor or PythonExecutor()
        self.data = (fn, args, kwargs)
        self.resources = resources
        self.retries = retries
        self.attempt = 1

        self.labels = Message(labels=Message(key='python'))

    def __call__(self):
        fn, args, kwargs = self.data
        return fn(*args, **kwargs)

    def retry(self, status):
        if self.attempt < self.retries:
            log.info('Task {} attempt #{} rescheduled due to failure with state '
                         '{} and message {}'.format(self.id, self.attempt,
                                                    status.state, status.message))
            self.attempt += 1
            status.state = 'TASK_STAGING'
        else:
            log.error('Aborting due to task {} failed for {} attempts in state '
                          '{} with message {}'.format(self.id, self.retries,
                                                      status.state, status.message))
            raise RuntimeError('Task {} failed with state {} and message {}'.format(
                self.id, status.state, status.message))

    def update(self, status):
        self.on_update(status)
        if status.has_succeeded():
            self.on_success(status)
        elif status.has_failed():
            self.on_fail(status)

    def on_update(self, status):
        self.status = status  # update task's status
        log.info('Task {} has been updated with state {}'.format(
            self.id.value, status.state))

    def on_success(self, status):
        log.info('Task {} has been succeded'.format(self.id.value))

    def on_fail(self, status):
        log.error('Task {} has been failed with state {} due to {}'.format(
            self.id.value, status.state, status.message))

        try:
            raise status.exception  # won't retry due to code error in PythonTaskStatus
        except KeyError as e:
            # not a code error, e.g. problem during deployment
            self.retry(status)
        else:
            log.error('Aborting due to task {} failed with state {} and message '
                          '{}'.format(self.id, status.state, status.message))


class PythonExecutor(Message):

 

    def __init__(self, docker='satyr', force_pull=False,
                 envs={}, uris=[], **kwds):
        super(PythonExecutor, self).__init__(**kwds)
        self.container = Message(
            type='MESOS',
            mesos=Message(
                image=Message(type='DOCKER',
                            docker=Message(name=docker))))
        self.command = Message(value='python -m satyr.executor',
                                   shell=True)
        self.force_pull = force_pull
        self.docker = docker
        self.envs = envs
        self.uris = uris

        self.labels = Message(labels=Message(key='python'))

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