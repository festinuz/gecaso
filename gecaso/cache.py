import asyncio

from . import utils
from . import storage


def cached(cache_storage, _loop=None, _hash_key=True, **params):
    """ Wraps function to cache its value in cache_storage.

    Positional arguments:
    cache_storage -- subclass of gecaso.BaseStorage used to store cached data

    Keyword arguments:
    _loop -- instance of event loop. asyncio.get_event_loop called otherwise
    _hash_key -- if True, any generated key will be a cache of fixed size
    **params -- passed to cache_storage.set each time its called
    """
    loop = _loop or asyncio.get_event_loop()
    if not isinstance(cache_storage, storage.BaseStorage):
        raise ValueError('Provided storage is not subclass of base storage')
    return _cached(cache_storage, loop, _hash_key, **params)


def _cached(cache_storage, loop, hash_key, **params):
    make_key = utils.hash_key if hash_key else utils.make_key

    def wrapper(function):
        current_calls = dict()

        async def wrapped_function(*args, **kwargs):
            key = make_key(function, *args, **kwargs)
            try:
                result = await cache_storage.get(key)
            except KeyError:
                if not current_calls.get(key):
                    future = asyncio.ensure_future(function(*args, **kwargs),
                                                   loop=loop)
                    current_calls[key] = future
                result = await current_calls[key]
                current_calls.pop(key, None)
                await cache_storage.set(key, result, **params)
            return result

        def sync_wrapped_function(*args, **kwargs):
            return loop.run_until_complete(wrapped_function(*args, **kwargs))

        if utils.is_async_function(function):
            return utils.wrap(function, wrapped_function)
        else:
            function = utils.asyncify(function)
            return utils.wrap(function, sync_wrapped_function)

    return wrapper
