import asyncio
import inspect

from . import utils
from . import storage


def cached(cache_storage, loop=None, **verfuns):
    func = utils.Namespace()
    loop = loop or asyncio.get_event_loop()
    if isinstance(cache_storage, storage.BaseStorage):
        async_storage = False
    elif isinstance(cache_storage, storage.BaseAsyncStorage):
        async_storage = True
    else:
        raise ValueError('Provided storage is not subclass of base storage')

    def ss_function(*args, **kwargs):
        key = utils.make_key(func.self, *args, **kwargs)
        try:
            result = cache_storage.get(key)
        except KeyError:
            result = func.self(*args, **kwargs)
            cache_storage.set(key, result, **verfuns)
        return result

    def sa_function(*args, **kwargs):
        key = utils.make_key(func.self, *args, **kwargs)
        try:
            result = loop.run_until_complete(cache_storage.get(key))
        except KeyError:
            result = func.self(*args, **kwargs)
            loop.run_until_complete(cache_storage.set(key, result, **verfuns))
        return result

    async def as_function(*args, **kwargs):
        key = utils.make_key(func.self, *args, **kwargs)
        try:
            result = cache_storage.get(key)
        except KeyError:
            result = await func.self(*args, **kwargs)
            cache_storage.set(key, result, **verfuns)
        return result

    async def aa_function(*args, **kwargs):
        key = utils.make_key(func.self, *args, **kwargs)
        try:
            result = await cache_storage.get(key)
        except KeyError:
            result = await func.self(*args, **kwargs)
            await cache_storage.set(key, result, **verfuns)
        return result

    def wrapper(function):
        func.self = function
        async_function = inspect.iscoroutinefunction(function)
        wrappers = {
            (False, False): ss_function,  # first letter tells if function
            (False, True):  sa_function,  # is asynchronous; second letter
            (True, False):  as_function,  # tells if cache storage is
            (True, True):   aa_function,  # asynchronous.
        }
        wrapped_function = wrappers[(async_function, async_storage)]
        return utils.wrap(function, wrapped_function)

    return wrapper
