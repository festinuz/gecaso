import abc
import time
import pickle

from . import utils


class BaseStorage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, key):
        """Must throw KeyError if key is not found"""
        pass

    @abc.abstractmethod
    def set(self, key, value, **params):
        pass

    def pack(self, value, **params):
        result = utils.Namespace(value=value, params=params)
        return pickle.dumps(result)

    def unpack(self, value):
        result = pickle.loads(value)
        return result.value, result.params

    def verified_get(self, value, **params):
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

    def vfunc_ttl(self, time_of_death):
        return time_of_death > time.time()
