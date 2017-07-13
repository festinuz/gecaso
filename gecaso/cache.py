import time
import pickle
import inspect
import functools


class _CacheDataWrapper:
    def __init__(self, data, ttl=None):
        self.data = data
        self.tod = time.time() + ttl  # time of death


def _make_key(function, *args, **kwargs):
    name_and_args = (function.__qualname__,) + tuple(a for a in args)
    return functools._make_key(name_and_args, kwargs, False)


def cached(cache_storage, ttl=None):
    func = dict(self=None, is_async=None)

    def get_cached(*args, **kwargs):
        key = _make_key(func['self'], *args, **kwargs)
        is_cached = False
        result = None
        c_result = cache_storage.get(key)
        if c_result:
            c_result = pickle.loads(c_result)
            if not c_result.tod or c_result.tod > time.time():
                is_cached = True
                result = c_result.data
        return key, is_cached, result

    def cache_result(key, result):
        wrapped_result_bytes = pickle.dumps(_CacheDataWrapper(result, ttl))
        cache_storage.set(key, wrapped_result_bytes)

    def cached_function(*args, **kwargs):
        key, is_cached, result = get_cached(*args, **kwargs)
        if not is_cached:
            result = func['self'](*args, **kwargs)
            cache_result(key, result)
        return result

    async def async_cached_function(*args, **kwargs):
        key, is_cached, result = get_cached(*args, **kwargs)
        if not is_cached:
            result = await func['self'](*args, **kwargs)
            cache_result(key, result)
        return result

    def wrapper(function):
        func['self'] = function
        func['is_async'] = inspect.iscoroutinefunction(function)
        if func['is_async']:
            return functools.wraps(function)(async_cached_function)
        else:
            return functools.wraps(function)(cached_function)

    return wrapper
