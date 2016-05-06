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
