import abc
import time
import pickle

from . import utils


class BaseStorage(metaclass=abc.ABCMeta):
    """Any storage that is to be passed to 'cache' wrapper should be inherited
    from this class.
    """
    @abc.abstractmethod
    def get(self, key):
        """Must throw KeyError if key is not found"""
        pass

    @abc.abstractmethod
    def set(self, key, value, **params):
        pass

    @abc.abstractmethod
    def remove(self, *keys):
        pass

    def pack(self, value, **params):
        """Packs value and methods into a object which is then converted to
        bytes using pickle library. Used to simplify storaging because bytes
        can bestored almost anywhere.
        """
        result = utils.Namespace(value=value, params=params)
        return pickle.dumps(result)

    def unpack(self, value):
        """Unpacks bytes object packed with 'pack' method. Returns packed value
        and parameters.
        """
        result = pickle.loads(value)
        return result.value, result.params

    def verified_get(self, value, **params):
        """Given value and params, returns value if all methods called from
        params (method name is assumed as 'vfunc_PARAMNAME' and argument is
        value of param) return 'True'; Else raises KeyError."""
        if all([getattr(self, 'vfunc_'+f)(v) for f, v in params.items()]):
            return value
        else:
            raise KeyError('Cached result didnt pass verification')


class LocalMemoryStorage(BaseStorage):
    def __init__(self):
        self._storage = dict()

    def get(self, key):
        value, params = self.unpack(self._storage[key])
        return self.verified_get(value, **params)

    def set(self, key, value, ttl=None):
        params = dict()
        if ttl:
            params['ttl'] = time.time() + ttl
        self._storage[key] = self.pack(value, **params)

    def remove(self, *keys):
        for key in keys:
            self._storage.pop(key, None)

    def vfunc_ttl(self, time_of_death):
        return time_of_death > time.time()


class LRUStorage(BaseStorage):
    """Storage that provides LRUCache functionality when used with 'cached'
    wrapper. If 'storage' argument is not provided, LocalMemoryStorage is used
    as default substorage. Any provided storage is expected to be inherited
    from BaseStorage.
    """
    class Node:
        def __init__(self, next_node=None, key=None):
            if next_node:
                self.prev = next_node.prev
                self.next = next_node.prev.next

                self.next.prev = self
                self.prev.next = self
            else:
                self.next = self
                self.prev = self
            self.key = key

        def delete(self):
            self.prev.next = self.next
            self.next.prev = self.prev

    def __init__(self, storage=None, maxsize=128):
        self._storage = storage or LocalMemoryStorage()
        self._nodes = dict()
        self._maxsize = maxsize
        self._head = LRUStorage.Node()  # This empty node will always be last
        self.storage_set = utils.asyncify(self._storage.set)
        self.storage_get = utils.asyncify(self._storage.get)
        self.storage_remove = utils.asyncify(self._storage.remove)

    async def get(self, key):
        node = self._nodes.pop(key)  # Throws KeyError on failure
        node.delete()
        value = await self.storage_get(key)  # Throws KeyError on failure
        self._nodes[key] = LRUStorage.Node(self._head, key)
        self._head = self._nodes[key]
        return value

    async def set(self, key, value, **params):
        if len(self._nodes) > self._maxsize:
            last_node = self._head.prev.prev  # skipping over empty node
            await self.remove(last_node.key)
        await self.storage_set(key, value, **params)
        self._nodes[key] = LRUStorage.Node(self._head, key)
        self._head = self._nodes[key]

    async def remove(self, key):
        node = self._nodes.pop(key)
        node.delete()
        await self.storage_remove(key)
