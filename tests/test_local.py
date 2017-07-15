import time
import asyncio

import pytest

import gecaso


class LocalAsyncMemoryStorage(gecaso.BaseAsyncStorage):
    def __init__(self):
        self._storage = dict()

    async def get(self, key):
        return self.retrieve(self._storage[key])

    async def set(self, key, value, **verfuncs):
        self._storage[key] = self.pack(value, **verfuncs)


local_storage = gecaso.LocalMemoryStorage()
local_async_storage = LocalAsyncMemoryStorage()


def long_function(time_to_sleep):
    time.sleep(time_to_sleep)
    return time_to_sleep


async def long_async_function(time_to_sleep):
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep


@pytest.mark.parametrize("storage", [local_storage, local_async_storage])
def test_local_sync_function_cache(storage):
    function = gecaso.cached(storage, ttl=5)(long_function)
    start_time = time.time()
    for i in range(5):
        assert function(2) == 2
    assert time.time() - start_time < 5


@pytest.mark.parametrize("storage", [local_storage, local_async_storage])
def test_local_async_function_cache(storage):
    function = gecaso.cached(storage, ttl=5)(long_async_function)
    loop = asyncio.get_event_loop()
    start_time = time.time()
    for i in range(5):
        assert loop.run_until_complete(function(2)) == 2
    assert time.time() - start_time < 5
