from satyr import log
from toolz import curry
from functools import wraps
import inspect


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
            log.exception(e)
            exception_sender.send(e)
    return f
