import time
import pickle
import asyncio
import inspect
import functools

from . import storage


class CacheDataWrapper:
    def __init__(self, data, ttl=None):
        self.data = data
        self.tod = time.time() + ttl  # time of death


def make_key(function, *args, **kwargs):
    name_and_args = (function.__qualname__,) + tuple(a for a in args)
    return functools._make_key(name_and_args, kwargs, False)


def retrieve_cached_result(cached_result):
    is_cached = False
    result = None
    if cached_result:
        cached_result = pickle.loads(cached_result)
        if not cached_result.tod or cached_result.tod > time.time():
            is_cached = True
            result = cached_result.data
    return is_cached, result


def pack_to_store(result, ttl):
    return pickle.dumps(CacheDataWrapper(result, ttl))


def cached(cache_storage, ttl=None, loop=None):
    func = dict(self=None, is_async=None)
    loop = loop or asyncio.get_event_loop()
    if isinstance(cache_storage, storage.BaseStorage):
        async_storage = False
    elif isinstance(cache_storage, storage.BaseAsyncStorage):
        async_storage = True
    else:
        raise ValueError('Provided storage is not subclass of base storage')

    def ss_function(*args, **kwargs):
        key = make_key(func['self'], *args, **kwargs)
        cached_data = cache_storage.get(key)
        is_cached, result = retrieve_cached_result(cached_data)
        if not is_cached:
            result = func['self'](*args, **kwargs)
            cache_storage.set(key, pack_to_store(result, ttl))
        return result

    def sa_function(*args, **kwargs):
        key = make_key(func['self'], *args, **kwargs)
        cached_data = loop.run_until_complete(cache_storage.get(key))
        is_cached, result = retrieve_cached_result(cached_data)
        if not is_cached:
            result = func['self'](*args, **kwargs)
            loop.run_until_complete(
                   cache_storage.set(key, pack_to_store(result, ttl)))
        return result

    async def as_function(*args, **kwargs):
        key = make_key(func['self'], *args, **kwargs)
        cached_data = cache_storage.get(key)
        is_cached, result = retrieve_cached_result(cached_data)
        if not is_cached:
            result = await func['self'](*args, **kwargs)
            cache_storage.set(key, pack_to_store(result, ttl))
        return result

    async def aa_function(*args, **kwargs):
        key = make_key(func['self'], *args, **kwargs)
        cached_data = await cache_storage.get(key)
        is_cached, result = retrieve_cached_result(cached_data)
        if not is_cached:
            result = await func['self'](*args, **kwargs)
            await cache_storage.set(key, pack_to_store(result, ttl))
        return result

    def wrapper(function):
        func['self'] = function
        func['is_async'] = inspect.iscoroutinefunction(function)
        wrappers = {
            (False, False): ss_function,  # first letter tells if function
            (False, True):  sa_function,  # is asynchronous; second letter
            (True, False):  as_function,  # tells if cache storage is
            (True, True):   aa_function,  # asynchronous.
        }
        wrapped = wrappers[(func['is_async'], async_storage)]
        return functools.wraps(function)(wrapped)

    return wrapper
