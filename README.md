# Gecaso

![master branch status](https://api.travis-ci.org/festinuz/gecaso.svg?branch=master)

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

    def get(self, key):
        value, params = self.unpack(self._storage[key])
        return value

    def set(self, key, value, **params):
        self._storage[key] = self.pack(value, **params)

    def remove(self, *keys):
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
##### Gecaso was created to be a simple solution that can be easily expanded to cover any needs of its users. Below is everything there is to know about using Gecaso. As such, there are only two objects that you need to know:

#### 1) "cached" function
This function is a wrapper that helps to set up cache for any synchronus or asynchronous function. It takes single positional argument, which must be an instance of class that is inherited from **BaseStorage**. It can also optionally be provided with a keyword argument **loop** which must be an instance of an event loop. Any keyword arguments provided besides **loop** will be passed to the **set** method of storage instance whenever it is being called.

#### 2) "BaseStorage" class
Any storage provided to "cached" function shoud be inherited from this class. Base storage has 6 methods.

* **get(self, key)**:  Abstract method that should be overriden. Can be synchronus or asynchronous. MUST raise KeyError if key is not present in storage. If data was packed using **pack** method before being stored, it must be unpacked using **unpack** method.

* **set(self, key, value, \*\*params)**: Abstract method that should be overriden. Can be synchronus or asynchronous. It is recomended to pack provided value using **pack** method before storing it in storage.

* **remove(self, \*keys)**: Abstract method that should be overriden. Should delete every key that is passed in *keys* parameter and exisits in storage.

* **pack(self, value, \*\*params)**: Returns representation of object with fields named *data* and *params* as bytes object.

* **unpack(self, value)**: Unpacks bytes object that was packed with **pack** method and returns *tuple(data, params)*.

* **verified_get(self, value, \*\*params)**: Helper function to run verification functions of storage. When provided with value and params, it will try to run a method of the class named **vfunc_PARAM** with value specified for that param for every param in *\*\*params*. See *Storage creation* for example of usage.


### Storage creation
##### The process of using gecaso library usually includes creating a storage that fits your specific task the most. Here is a step by step example that should help you understand this process.

Lets say that we want to have in-memory cache with the option of specifying *"time to live"* for cached results. Here are the steps we would take:

1) Import gecaso and create the base of our class:
```python
import time
import gecaso

class LocalMemoryStorage(gecaso.BaseStorage):
    def __init__(self):
        self._storage = dict()  # Python's dict is a nice basic storage of data
```

2) Override **set**, **get** and **remove** methods of gecaso.BaseStorage:
```python
    def set(self, key, value, ttl=None):  # We dont want any additional parameters besides time to live
        params = dict()
        if ttl:  # We want ttl to be an optional parameter
            params['ttl'] = time.time() + ttl  # Calculate time_of_death,after which result is considered invalid
        self._storage[key] = self.pack(value, **params)  # Using BaseStorage.pack method

    def get(self, key):
        self.data = self._storage[key]  # If key is not present this will raise KeyError
        value, params = self.unpack(self._storage[key])  # params can optionally contain ttl
        return self.verified_get(value, **params)  # Using BaseStorage.verified_get method to verify ttl

    def remove(self, *keys):
        for key in keys:
            self._storage.pop(key, None)  # Not going to throw error if some of the keys do not exists
```
At this point the get method wont work properly because we called **verified_get** at the end of it. This method tries to call class method for every parameter it got and will break since we are trying to pass it our **ttl** parameter but it cant find the verifying function that this parameter should represent.

3) Write a verifying function for our ttl parameter:
```python
    def vfunc_ttl(self, time_of_death):
    """Note that the name of this function is equivalent of 'vfunc_' + parameter_name """
        return time_of_death > time.time()
```

And now we're done! Whenever we request a value using **get** method it will eventually call **verified_get** which will return value if all the verifying functions returned true and will raise **KeyError** otherwise.

After the storage class has been created, all that is left to do is create an instance of this class and provide it to **cached** decorator whenever it is being called:

```python
local_storage = LocalMemoryStorage()

@gecaso.cached(local_storage, ttl=30)
def foo(bar):
    pass
```
