from __future__ import absolute_import, division, print_function

import signal
from contextlib import contextmanager


def partition(pred, iterable):
    trues, falses = [], []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses


class TimeoutError(Exception):
    pass


@contextmanager
def timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError("Timed out!")

    if seconds > 0:
        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:  # infinite timeout
        yield


class SignalHandler(object):

    def __init__(self, handler, signals=(signal.SIGINT, signal.SIGTERM)):
        self.handler = handler
        self.signals = signals
        self.original_handlers = {}

    def register(self):
        def signal_handler(signum, frame):
            self.release()
            self.handler()

        self.released = False
        for sig in self.signals:
            self.original_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, signal_handler)

    def release(self):
        if self.released:
            return False

        for sig in self.signals:
            signal.signal(sig, self.original_handlers[sig])

        self.released = True
        return True

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
        if exc_type:
            raise exc_type, exc_value, traceback


class Interruptable(object):

    def __init__(self):
        self.signal_handler = SignalHandler(self.stop)

    def start(self):
        self.signal_handler.register()
        return super(Interruptable, self).stop()

    def stop(self):
        self.signal_handler.release()
        return super(Interruptable, self).stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.join()
        if exc_type:
            raise exc_type, exc_value, traceback


class RemoteException(Exception):
    """ Remote Exception

    Contains the exception and traceback from a remotely run task
     - Include the original error message
     - Respond to try-except blocks with original error type
     - Include remote traceback
    """

    def __init__(self, exception, traceback):
        self.exception = exception
        self.traceback = traceback

    def __str__(self):
        return (str(self.exception) + "\n\n"
                "Traceback\n"
                "---------\n" +
                self.traceback)

    def __dir__(self):
        return sorted(set(dir(type(self)) +
                          list(self.__dict__) +
                          dir(self.exception)))

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            return getattr(self.exception, key)


exceptions = dict()


def remote_exception(exc, tb):
    """ Metaclass that wraps exception type in RemoteException """
    if type(exc) in exceptions:
        typ = exceptions[type(exc)]
        return typ(exc, tb)
    else:
        try:
            typ = type(exc.__class__.__name__,
                       (RemoteException, type(exc)),
                       {'exception_type': type(exc)})
            exceptions[type(exc)] = typ
            return typ(exc, tb)
        except TypeError:
            return exc
