import time


def _ttl(tod):
    return tod > time.time()


def ttl(seconds):
    tod = time.time() + seconds
    return _ttl, tod
