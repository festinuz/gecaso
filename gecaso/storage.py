import abc
import pickle

from . import utils
from . import vfuncs


class DataWrapper:
    def pack(self, value, **verfuncs):
        result = utils.Namespace()
        result.value = value
        result.verfuncs = [getattr(vfuncs, f)(v) for f, v in verfuncs.items()]
        return pickle.dumps(result)

    def is_valid(self, result):
        return all([verfunc(value) for verfunc, value in result.verfuncs])

    def retrieve(self, data):
        result = pickle.loads(data)
        if self.is_valid(result):
            return result.value
        else:
            raise KeyError('Cached result didnt pass validation')


class BaseStorage(DataWrapper, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, key):
        """Must throw KeyError if key is not found"""
        pass

    @abc.abstractmethod
    def set(self, key, value, **verfuncs):
        pass


class BaseAsyncStorage(DataWrapper, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def get(self, key):
        """Must throw KeyError if key is not found"""
        pass

    @abc.abstractmethod
    async def set(self, key, value, **verfuncs):
        pass


class LocalMemoryStorage(BaseStorage):
    def __init__(self):
        self._storage = dict()

    def get(self, key):
        return self.retrieve(self._storage[key])

    def set(self, key, value, **verfuncs):
        self._storage[key] = self.pack(value, **verfuncs)
