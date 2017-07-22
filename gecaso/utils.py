import pickle
import inspect
import functools


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def make_key(function, *args, **kwargs):
    name_and_args = (function.__qualname__,) + tuple(a for a in args)
    return functools._make_key(name_and_args, kwargs, False)


def wrap(function, wrapped_function):
    return functools.wraps(function)(wrapped_function)


def is_async_function(function):
    return inspect.iscoroutinefunction(function)


def asyncify(function):
    """Wraps function. If function is asynchrounous, it is not changed.
    If function is synchronous, returns asynchrounous function which calls
    synchronous function inside. This function allows to write code that uses
    sync/async functions in the same manner: as async functions."""
    async def new_function(*args, **kwargs):
        if is_async_function(function):
            return await function(*args, **kwargs)
        else:
            return function(*args, **kwargs)
    return wrap(function, new_function)


def pack(value, **params):
    """Packs value and params into a object which is then converted to
    bytes using pickle library. Is used to simplify storaging because bytes
    can bestored almost anywhere.
    """
    result = Namespace(value=value, params=params)
    return pickle.dumps(result)


def unpack(value):
    """Unpacks bytes object packed with 'pack' function. Returns packed value
    and parameters.
    """
    result = pickle.loads(value)
    return result.value, result.params
