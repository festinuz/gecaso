import time
import asyncio
import inspect

import pytest

import gecaso


local_storage = gecaso.MemoryStorage()


def slow_echo(time_to_sleep):
    time.sleep(time_to_sleep)
    return time_to_sleep


async def slow_async_echo(time_to_sleep):
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep


@pytest.mark.parametrize("storage", [local_storage])
@pytest.mark.parametrize("echo_function", [slow_echo, slow_async_echo])
@pytest.mark.parametrize("argument", [2])
def test_local_function_cache(storage, echo_function, argument):
    slow_echo = gecaso.cached(storage)(echo_function)
    start_time = time.time()
    if inspect.iscoroutinefunction(slow_echo):
        loop = asyncio.get_event_loop()
        for i in range(5):
            assert loop.run_until_complete(slow_echo(argument)) == argument
    else:
        for i in range(5):
            assert slow_echo(argument) == argument
    assert time.time() - start_time < argument*2
