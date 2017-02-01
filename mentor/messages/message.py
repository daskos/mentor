""" Message attr dict implementation based on Bunch and Message
"""

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


class RegisterProxies(type):

    def __init__(cls, name, bases, nmspc):
        super(RegisterProxies, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = {}
        cls.registry[cls.key]=cls



class Message(dict,metaclass=RegisterProxies):
    """ A dictionary that provides attribute-style access.
    """
    key = "message"

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

    @classmethod
    def encode(cls,x):
        """ Recursively transforms a dictionary into a Message via copy.

        """
        if isinstance(x, dict):
            kwargs=[]
            for k,value in iteritems(x):
                if k in cls.registry:
                    c = cls.registry[k]
                    if isinstance(value, (list, tuple)):
                      kwargs.append( (k ,[c.encode(v) for v in value ]))
                    else:
                      kwargs.append((k, c.encode(value)))
                elif isinstance(value, dict):
                    kwargs.append((k, Message(value)))
                else:
                    kwargs.append((k,value))
            return cls.encode(kwargs)
            #return cls((k, cls.encode(v,cls)) for k, v in iteritems(x))
        # elif isinstance(x, (list, tuple)):
        #     return [cls.encode(v) for v in x]
        else:
            return cls(x)

    @classmethod
    def decode(cls,x):
        """ Recursively converts a Message into a dictionary.
        """
        if isinstance(x, dict):
            return dict((k, decode(v)) for k, v in iteritems(x))
        elif isinstance(x, (list, tuple)):
            return type(x)(decode(v) for v in x)
        else:
            return x

