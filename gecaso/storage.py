import abc
import time
import pickle

from . import utils


class DataWrapper:
    def pack(self, data, **params):
        result = utils.Namespace()
        result.data = data
        result.params = params
        return pickle.dumps(result)

    def unpack(self, data):
        return pickle.loads(data)

    def verify(self, params):
        return all([getattr(self, 'vfunc_'+f)(v) for f, v in params.items()])

    def verified_get(self, result):
        if self.verify(result.params):
            return result.data
        else:
            raise KeyError('Cached result didnt pass verification')


class BaseStorage(DataWrapper, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, key):
        """Must throw KeyError if key is not found"""
        pass

    @abc.abstractmethod
    def set(self, key, value, **params):
        pass


class LocalMemoryStorage(BaseStorage):
    def __init__(self):
        self._storage = dict()

    def get(self, key):
        result = self.unpack(self._storage[key])
        return self.verified_get(result)

    def set(self, key, value, ttl=None):
        params = dict()
        if ttl:
            params['ttl'] = time.time() + ttl
        self._storage[key] = self.pack(value, **params)

    def vfunc_ttl(self, time_of_death):
        return time_of_death > time.time()
