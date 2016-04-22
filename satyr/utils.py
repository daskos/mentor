from __future__ import absolute_import, division, print_function

# import atexit
# from . import log as logging
import inspect
import json
import logging
import multiprocessing as mp
import os
import signal
import sys
import time
from copy import copy
from functools import wraps

from colorlog import ColoredFormatter
from toolz import curry


# TODO use python-daemon like luigi does
# https://github.com/spotify/luigi/blob/7db1ceadc4d3f8ef62eccffa1a6412bc747f8132/luigi/process.py#L78


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


# def catch(func, exception_sender):
#     """Closure that calls given func, if an error is raised, send it somewhere.

#     `func` function to call
#     `exception_sender` a writable end of a multiprocessing.Pipe
#     """
#     def f(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except Exception as e:
#             logging.exception(e)
#             exception_sender.send(e)
#     return f


# def set_signals(process):
#     """Kill child processes on sigint or sigterm"""
#     def kill_children(signal, frame):
#         logging.error('Received a signal that is trying to terminate this '
#                       'thread.', extra=dict(signal=signal))
#         try:
#             driver.stop()
#             logging.info('terminated thread',
#                          extra=dict(name=process.name, pid=process.pid))
#         except:
#             logging.exception('could not terminate thread',
#                               extra=dict(name=process.name, pid=process.pid))
#         sys.exit(1)
#     signal.signal(signal.SIGTERM, kill_children)
#     signal.signal(signal.SIGINT, kill_children)


# def run_daemon(name, target, kwargs=dict()):
#     #exception_receiver, exception_sender = mp.Pipe(False)

#     thread = Thread(target=target, kwargs=kwargs, name=name)
#     thread.start()
#     set_signals(thread)

#     return thread
#     # return subproc

#     # while True:
#     #     if exception_receiver.poll():
#     #         exception_receiver.recv()
#     #         logging.error('Terminating child process because it raised an '
#     #                       'exception', extra=dict(is_alive=subproc.is_alive()))
#     #         break
#     #     if not subproc.is_alive():
#     #         logging.error('Daemon process died and didn\'t notify me of its '
#     #                       'exception. This may be a code bug. Check logs!',
#     #                       extra=dict())
#     #         break
#     #     # save cpu cycles by checking for subprocess failures less often
#     #    time.sleep(1)

#     # subproc.terminate()
#     # sys.exit(1)


def configure_logging(add_handler, log):
    """
    Configure log records.  If adding a handler, make the formatter print all
    passed in key:value data.
        ie log.extra('msg', extra=dict(a=1))
        generates  'msg  a=1'
    `add_handler` (True, False, None, or Handler instance)
        if True, add a logging.StreamHandler() instance
        if False, do not add any handlers.
        if given a handler instance, add that the the logger
    """
    _ignore_log_keys = set(logging.makeLogRecord({}).__dict__)

    def _json_format(record):
        extras = ' '.join(
            "%s=%s" % (k, record.__dict__[k])
            for k in set(record.__dict__).difference(_ignore_log_keys))
        if extras:
            record.msg = "%s    %s" % (record.msg, extras)
        return record

    class ColoredJsonFormatter(ColoredFormatter):

        def format(self, record):
            record = _json_format(record)
            return super(ColoredJsonFormatter, self).format(record)
    if isinstance(add_handler, logging.Handler):
        log.addHandler(add_handler)
    elif add_handler is True:
        if not any(isinstance(h, logging.StreamHandler) for h in log.handlers):
            _h = logging.StreamHandler()
            _h.setFormatter(ColoredJsonFormatter(
                "%(log_color)s%(levelname)-8s %(message)s %(reset)s %(cyan)s",
                reset=True
            ))
            log.addHandler(_h)
    elif not log.handlers:
        log.addHandler(logging.NullHandler())
    log.setLevel(logging.DEBUG)
    log.propagate = False
    return log


def add_zmq_log_handler(address):
    import zmq.log.handlers

    class JSONPubHandler(zmq.log.handlers.PUBHandler):

        def format(self, record):
            return json.dumps(record.__dict__)

    sock = zmq.Context().socket(zmq.PUB)
    sock.connect(address)
    handler = JSONPubHandler(sock)
    return configure_logging(handler)
