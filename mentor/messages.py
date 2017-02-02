import operator
import copy
a = {'agent_id': {'value': '4ddc596d-4dca-4e9d-a906-21cba8736ba5-S0'}, 'attributes': [{'name': 'mentos', 'text': {'value': 'true'}, 'type': 'TEXT'}], 'framework_id': {'value': '4ddc596d-4dca-4e9d-a906-21cba8736ba5-0001'}, 'hostname': 'malefico.io', 'id': {'value': '4ddc596d-4dca-4e9d-a906-21cba8736ba5-O6'}, 'resources': [{'name': 'cpus', 'role': '*', 'scalar': {'value': 0.5}, 'type': 'SCALAR'}, {'name': 'mem', 'role': '*', 'scalar': {'value': 128.0}, 'type': 'SCALAR'}, {'name': 'ports', 'ranges': {'range': [{'begin': 11000, 'end': 11999}]}, 'role': '*', 'type': 'RANGES'}, {'name': 'disk', 'role': '*', 'scalar': {'value': 0.0}, 'type': 'SCALAR'}], 'url': {'address': {'hostname': 'malefico.io', 'ip': '127.0.0.1', 'port': 5052}, 'path': '/slave(1)', 'scheme': 'http'}}


b =  {'task_id': {'value': '987ede91-81f1-491c-a7db-1c8de54b8c92'}, 'agent_id': {'value': '4ddc596d-4dca-4e9d-a906-21cba8736ba5-S1'}, 'name': 'task 987ede91-81f1-491c-a7db-1c8de54b8c92', 'executor': {'executor_id': {'value': 'MinimalExecutor'}, 'name': 'MinimalExecutor', 'command': {'value': '/opt/anaconda3/envs/mentos/bin/python /home/arti/workdir/mesos/dmentos/examples/executor.py'}, 'resources': [{'name': 'mem', 'type': 'SCALAR', 'scalar': {'value': 32}}, {'name': 'cpus', 'type': 'SCALAR', 'scalar': {'value': 0.1}}]}, 'data': 'SGVsbG8gZnJvbSB0YXNrIDk4N2VkZTkxLTgxZjEtNDkxYy1hN2RiLTFjOGRlNTRiOGM5MiE=', 'resources': [{'name': 'cpus', 'type': 'SCALAR', 'scalar': {'value': 1}}, {'name': 'mem', 'type': 'SCALAR', 'scalar': {'value': 128}}]}

def cpus(message):
    for res in message.resources:
        if res.name == "cpus":
            return res
    return {'name': 'cpus', 'scalar': {'value': 0}}


def mem(message):
    for res in message.resources:
        if res.name == "mem":
            return res
    return {'name': 'mem', 'scalar': {'value': 0}}


def disk(message):
    for res in message.resources:
        if res.name == "disk":
            return res
    return {'name': 'disk', 'scalar': {'value': 0}}


import six

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


class ResourceMixin(object):

    zeroes = {'cpus': 0.0, 'mem': 0.0, 'disk': 0.0, 'ports': 0.0} # gpu

    @staticmethod
    def flatten(message):
        flattened = {}
        for r in message['resources']:
            if r["type"]=="RANGES":
               pass
            else:
                flattened[r['name']]=(r['scalar']['value'])
        return flattened

    def compare(self, op, other):
        a = self.flatten(self)
        b = self.flatten(other)
        return [op(a.get(k, v), b.get(k, v))
                for k, v in self.zeroes.items()]

    def __eq__(self, other):
        return all(self.compare(operator.eq, other))

    def __ne__(self, other):
        return all(self.compare(operator.ne, other))

    def __lt__(self, other):
        return all(self.compare(operator.lt, other))

    def __le__(self, other):
        return all(self.compare(operator.le, other))

    def __gt__(self, other):
        return any(self.compare(operator.gt, other))

    def __ge__(self, other):
        return any(self.compare(operator.ge, other))


    def __add__(self, second):
        mixin = copy.deepcopy(self)
        mixin.resources = self.compare(operator.add,second)
        return mixin

    def __sub__(self, second):
        mixin = copy.deepcopy(self)
        mixin.resources = self.compare(operator.sub,second)
        return mixin

    def __radd__(self, second):  # to support sum()

        return self + second

    def __iadd__(self, second):
        
        added = self + second
        self.resources = added.resources
        return self

    def __isub__(self, second):
        
        subbed = self - second
        self.resources = subbed.resources
        return self


class TaskInfo(ResourceMixin, Message):
    pass

class Offer(ResourceMixin, Message):
    pass


A = Offer(a)
B = TaskInfo(b)

#assert A != B  # False
# assert A > B   # False
# assert A <= B  # True
# assert A < B   # False
# assert A <= B  # False
A>B
a=A-B