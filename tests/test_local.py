import time
import asyncio

import gecaso


class LocalAsyncMemoryStorage(gecaso.BaseAsyncStorage):
    def __init__(self):
        self.storage = dict()

    async def get(self, key, default=None):
        return self.storage.get(key, default)

    async def set(self, key, value):
        self.storage[key] = value

    async def remove(self, key):
        self.storage.pop(key)


local_storage = gecaso.LocalMemoryStorage()
local_async_storage = LocalAsyncMemoryStorage()


@gecaso.cached(local_storage, ttl=5)
def long_function(time_to_sleep):
    time.sleep(time_to_sleep)
    return time_to_sleep


@gecaso.cached(local_storage, ttl=5)
async def long_async_function(time_to_sleep):
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep


@gecaso.cached(local_async_storage, ttl=5)
def another_long_function(time_to_sleep):
    time.sleep(time_to_sleep)
    return time_to_sleep


@gecaso.cached(local_async_storage, ttl=5)
async def another_long_async_function(time_to_sleep):
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep


def test_ss_wrapping():
    start_time = time.time()
    for i in range(10):
        assert long_function(2) == 2
    assert time.time() - start_time < 5


def test_as_wrapping():
    loop = asyncio.get_event_loop()
    start_time = time.time()
    for i in range(10):
        assert loop.run_until_complete(long_async_function(2)) == 2
    assert time.time() - start_time < 5


def test_sa_wrapping():
    start_time = time.time()
    for i in range(10):
        assert another_long_function(2) == 2
    assert time.time() - start_time < 5


def test_aa_wrapping():
    loop = asyncio.get_event_loop()
    start_time = time.time()
    for i in range(10):
        assert loop.run_until_complete(another_long_async_function(2)) == 2
    assert time.time() - start_time < 5
