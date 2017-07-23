import asyncio

import gecaso


@gecaso.cached(gecaso.MemoryStorage())
async def slow_echo(time_to_sleep):
    slow_echo.called += 1
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep


slow_echo.called = 0


def test_dogpile_fix():
    tasks = asyncio.gather(*[slow_echo(2) for i in range(10)])
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(tasks))
    print(slow_echo.called)
    assert slow_echo.called == 1
