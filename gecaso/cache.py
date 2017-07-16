import asyncio

from . import utils
from . import storage


def cached(cache_storage, loop=None, **params):
    loop = loop or asyncio.get_event_loop()
    if not isinstance(cache_storage, storage.BaseStorage):
        raise ValueError('Provided storage is not subclass of base storage')
    return _cached(cache_storage, loop, **params)


def _cached(cache_storage, loop, **params):
    storage_get = utils.asyncify(cache_storage.get)
    storage_set = utils.asyncify(cache_storage.set)

    def wrapper(function):
        async def wrapped_function(*args, **kwargs):
            key = utils.make_key(function, *args, **kwargs)
            try:
                result = await storage_get(key)
            except KeyError:
                result = await function(*args, **kwargs)
                await storage_set(key, result)
            return result

        def sync_wrapped_function(*args, **kwargs):
            return loop.run_until_complete(wrapped_function(*args, **kwargs))

        if utils.is_async_function(function):
            return utils.wrap(function, wrapped_function)
        else:
            function = utils.asyncify(function)
            return utils.wrap(function, sync_wrapped_function)

    return wrapper
