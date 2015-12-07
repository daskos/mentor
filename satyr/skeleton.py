from mesos.interface import mesos_pb2
import types, sys


class Skeleton(object):
    ALLOWED_HANDLERS = []

    def __getattr__(self, name):
        """Automatically log some info about unused methods like:
        registered, reregistered, disconnected, offer_rescinded,
        slave_lost, executor_lost, error.

        Also note that this will run on every access for non-existent attributes
        so be careful w/ it.
        """

        print 'Tried to access member method [%s]' % name

        def handler(*args, **kwargs):
            print 'Event [%s] triggered (%s) (%s)' % (name, args, kwargs)

        return handler

    #def __getattribute__(self, name):
        #print '[[[[[[ %s ]]]]]]' % name
        #return object.__getattribute__(self, name)

    def add_handler(self, name, method):
        if name not in self.ALLOWED_HANDLERS:
            raise ValueError('You are not allowed to set such a handler: %s' % name)

        self.__dict__[name] = types.MethodType(method, self)
        self.__dict__[name.title().replace('_', '')] = types.MethodType(method, self) # yo, bitch! :'(
        print 'Handler added [%s]' % name


def create_driver_method(driver):
    def method():
        status = 0 if driver.run() == mesos_pb2.DRIVER_STOPPED else 1
        driver.stop()
        sys.exit(status)

    return method
