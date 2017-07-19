import time
import asyncio
import inspect

import pytest

import gecaso


class LocalAsyncMemoryStorage(gecaso.BaseStorage):
    def __init__(self):
        self._storage = dict()

    async def get(self, key):
        value, params = self.unpack(self._storage[key])
        return self.verified_get(value, **params)

    async def set(self, key, value, ttl=None):
        params = dict()
        if ttl:
            params['ttl'] = time.time() + ttl
        self._storage[key] = self.pack(value, **params)

    async def remove(self, *keys):
        for key in keys:
            self._storage.pop(key, None)

    def vfunc_ttl(self, time_of_death):
        return time_of_death > time.time()


def slow_echo(time_to_sleep):
    time.sleep(time_to_sleep)
    return time_to_sleep


async def slow_async_echo(time_to_sleep):
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep


local_storage = gecaso.LocalMemoryStorage()
local_async_storage = LocalAsyncMemoryStorage()


@pytest.mark.parametrize("storage", [local_storage, local_async_storage])
@pytest.mark.parametrize("echo_func", [slow_echo, slow_async_echo])
def test_lru_cache(storage, echo_func):
    lru_echo = gecaso.cached(gecaso.LRUStorage(storage, maxsize=4))(echo_func)
    start_time = time.time()
    if inspect.iscoroutinefunction(lru_echo):
        loop = asyncio.get_event_loop()
        assert loop.run_until_complete(lru_echo(0.5)) == 0.5
        assert loop.run_until_complete(lru_echo(0.4)) == 0.4
        assert loop.run_until_complete(lru_echo(0.3)) == 0.3
        assert loop.run_until_complete(lru_echo(0.2)) == 0.2
        assert loop.run_until_complete(lru_echo(0.1)) == 0.1
        assert loop.run_until_complete(lru_echo(0.0)) == 0.0
        for i in range(10):
            assert loop.run_until_complete(lru_echo(0.3)) == 0.3
        assert loop.run_until_complete(lru_echo(0.5)) == 0.5
    else:
        assert lru_echo(0.5) == 0.5
        assert lru_echo(0.4) == 0.4
        assert lru_echo(0.3) == 0.3
        assert lru_echo(0.2) == 0.2
        assert lru_echo(0.1) == 0.1
        assert lru_echo(0.0) == 0.0
        for i in range(10):
            assert lru_echo(0.3) == 0.3
        assert lru_echo(0.5) == 0.5
        assert lru_echo(0.01) == 0.01
        assert lru_echo(0.02) == 0.02
        assert lru_echo(0.03) == 0.03
        assert lru_echo(0.04) == 0.04
    assert 2 < time.time() - start_time < 2.5
