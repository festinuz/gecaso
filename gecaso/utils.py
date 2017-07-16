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


def asyncify(function):
    async def new_function(*args, **kwargs):
        if inspect.iscoroutinefunction(function):
            return await function(*args, **kwargs)
        else:
            return function(*args, **kwargs)
    return wrap(function, new_function)
