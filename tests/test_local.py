import time
import asyncio

import gecaso


local_storage = gecaso.LocalMemoryStorage()


@gecaso.cached(local_storage, ttl=5)
def long_function(time_to_sleep):
    time.sleep(time_to_sleep)
    return time_to_sleep


@gecaso.cached(local_storage, ttl=5)
async def long_async_function(time_to_sleep):
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep


def test_memory_storage_on_long_function():
    start_time = time.time()
    for i in range(10):
        assert long_function(2) == 2
    assert time.time() - start_time < 5


def test_memory_storage_on_long_async_function():
    loop = asyncio.get_event_loop()
    start_time = time.time()
    for i in range(10):
        assert loop.run_until_complete(long_async_function(2)) == 2
    assert time.time() - start_time < 5
