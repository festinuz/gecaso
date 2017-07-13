import abc


class BaseStorage:
    @abc.abstractmethod
    def get(self, key, default=None):
        pass

    @abc.abstractmethod
    def set(self, key, value):
        """It should be possible for value to be of type 'bytes'."""
        pass

    @abc.abstractmethod
    def remove(self, key):
        pass


class LocalMemoryStorage(BaseStorage):
    def __init__(self):
        self.storage = dict()

    def get(self, key, default=None):
        return self.storage.get(key, default)

    def set(self, key, value):
        self.storage[key] = value

    def remove(self, key):
        self.storage.pop(key)
