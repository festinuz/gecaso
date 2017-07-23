# Gecaso

[![PyPI version](https://badge.fury.io/py/gecaso.svg)](https://badge.fury.io/py/gecaso) ![master branch status](https://api.travis-ci.org/festinuz/gecaso.svg?branch=master)

Gecaso provides you with the tools that help with creating cache for your specific task.

### Examples

#### Using default gecaso storages
```python
import gecaso


@gecaso.cached(LRUStorage(maxsize=16), ttl=100)
def long_and_boring_function(time_to_sleep):
    time.sleep(time_to_sleep)
    return f'I have slept for {time_to_sleep} second(s)!'
```

#### Creating new storage to fit your task
Lets say you want to cache the result of some of your functions using Redis. All you need to do is write a simple class in which you specify the steps for setting and getting data from redis.

1) Create a Redis storage:
```python
import redis
import gecaso


class RedisStorage(gecaso.BaseStorage):
    def __init__(self, redis_url):
        self._storage = redis.from_url(redis_url)

    async def get(self, key):
        value, params = gecaso.unpack(self._storage[key])
        return value

    async def set(self, key, value, **params):
        self._storage[key] = gecaso.pack(value, **params)

    async def remove(self, *keys):
        self._storage.remove(*keys)

redis_storage = RedisStorage('valid_redis_url')
```
2) Set your cache for any function you want:

```python
@gecaso.cached(redis_storage, some_additional_cool_param='Hell yeah!')
def long_and_boring_function(time_to_sleep):
    time.sleep(time_to_sleep)
    return f'I have slept for {time_to_sleep} second(s)!'
```

## Installation
Install gecaso with pip:
```
    pip install gecaso
```
Note that at the time, gecaso only supports versions of python that are >=3.5

## Usage Guide
##### Gecaso was created to be a simple solution that can be easily expanded to cover any needs of its users. Below is everything there is to know about using Gecaso.

#### 1) "gecaso.cached" function
This function is a wrapper that helps to set up cache for any synchronus or asynchronous function. It takes single positional argument, which must be an instance of class that is inherited from **BaseStorage**. It can also optionally be provided with a keyword argument **loop** which must be an instance of an event loop. Any keyword arguments provided besides **loop** will be passed to the **set** method of storage instance whenever it is being called.

#### 2) "gecaso.BaseStorage" class
Any storage provided to "cached" function should be inherited from this class. Base storage has 6 methods.

* **get(self, key)**:  Abstract method that should be overridden. Must be asynchronous. MUST raise KeyError if key is not present in storage. If data was packed using **gecaso.pack** function before being stored, it must be unpacked using **gecaso.unpack** function.

* **set(self, key, value, \*\*params)**: Abstract method that should be overridden. Must be asynchronous. It is recommended to pack provided value using **gecaso.pack** function before storing it in storage.

* **remove(self, \*keys)**: Abstract method that should be overridden. Must be asynchronous. Should delete every key that is passed in *keys* parameter and exists in storage.


#### 3) Helper functions
* **gecaso.pack(value, \*\*params)**: Returns representation of object with fields named *data* and *params* as bytes object. Useful when creating a custom storage as it allows to store almost anything as 'bytes'.

* **gecaso.unpack(value)**: Unpacks bytes object that was packed with **pack** method and returns *tuple(data, params)*.


#### 4) Storages provided by gecaso library
* **gecaso.MemoryStorage** storages all the data in RAM. Can be used as a default storage.
* **gecaso.LRUStorage** is a simplified implementation that provides LRU cache functionality. Storage passed to its *\_\_init\_\_()* method will be used used to store values. This effectively allows to wrap any preexisting storage in *gecaso.LRUStorage* to get LRU cache functionality for that storage.

### Storage creation
##### The process of using gecaso library usually includes creating a storage that fits your specific task the most. Here is a step by step example that should help you understand this process.

Lets say that we want to have a simple in-memory cache. Here are the steps we would take:

1) Import gecaso and create the base of our class:
```python
import gecaso

class LocalMemoryStorage(gecaso.BaseStorage):
    def __init__(self):
        self._storage = dict()  # Python's dict is a nice basic storage of data
```

2) Override async methods **set**, **get** and **remove** of gecaso.BaseStorage:
```python
    async def set(self, key, value):  # We don't want any additional parameters
        params = dict()
        self._storage[key] = gecaso.pack(value, **params)

    async def get(self, key):
        self.data = self._storage[key]  # If key is not present this will raise KeyError
        value, params = gecaso.unpack(self._storage[key])
        return value

    async def remove(self, *keys):
        for key in keys:
            self._storage.pop(key, None)  # Not going to throw error if some of the keys do not exists
```

And now we're done!
After the storage class has been created, all that is left to do is create an instance of this class and provide it to **cached** decorator whenever it is being called:

```python
local_storage = LocalMemoryStorage()

@gecaso.cached(local_storage)
def foo(bar):
    pass
```
