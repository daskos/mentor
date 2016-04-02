from __future__ import absolute_import, division, print_function


from toolz import curry
from functools import wraps
import inspect
import logging
import atexit
import signal
import time
import os
import sys
import multiprocessing as mp
#from . import log as logging

@curry
def envargs(fn, prefix='', envs=os.environ):
    spec = inspect.getargspec(fn)
    envs = {k: envs[prefix + k.upper()] for k in spec.args
            if prefix + k.upper() in envs}
    defs = dict(zip(spec.args[-len(spec.defaults):],
                    spec.defaults))
    defs.update(envs)

    @wraps(fn)
    def wrapper(*args, **kwargs):
        params = copy(defs)
        params.update(zip(spec.args[:len(args)], args))
        params.update(kwargs)
        return fn(**params)

    return wrapper


def catch(func, exception_sender):
    """Closure that calls given func.  If an error is raised, send it somewhere
    `func` function to call
    `exception_sender` a writable end of a multiprocessing.Pipe
    """
    def f(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logging.exception(e)
            exception_sender.send(e)
    return f


def set_signals(process):
    """Kill child processes on sigint or sigterm"""
    def kill_children(signal, frame):
        logging.error('Received a signal that is trying to terminate this '
                      'process.', extra=dict(signal=signal))
        try:
            process.terminate()
            logging.info('terminated process',
                         extra=dict(name=process.name, pid=process.pid))
        except:
            logging.exception('could not terminate subprocess',
                              extra=dict(name=process.name, pid=process.pid))
        sys.exit(1)
    signal.signal(signal.SIGTERM, kill_children)
    signal.signal(signal.SIGINT, kill_children)


def run_daemon(name, target, kwargs=dict()):
    exception_receiver, exception_sender = mp.Pipe(False)

    subproc = mp.Process(target=catch(target, exception_sender),
                         kwargs=kwargs,
                         name=name)
    subproc.start()
    set_signals(subproc)

    while True:
        if exception_receiver.poll():
            exception_receiver.recv()
            logging.error('Terminating child process because it raised an '
                          'exception', extra=dict(is_alive=subproc.is_alive()))
            break
        if not subproc.is_alive():
            logging.error('Mesos Scheduler died and didn\'t notify me of its '
                          'exception. This may be a code bug. Check logs.',
                          extra=dict())
            break
        # save cpu cycles by checking for subprocess failures less often
        time.sleep(1)

    subproc.terminate()
    sys.exit(1)
