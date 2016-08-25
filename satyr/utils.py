from __future__ import absolute_import, division, print_function

import signal
from contextlib import contextmanager


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
