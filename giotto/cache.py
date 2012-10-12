import pylibmc

class GiottoCache(object):
    def set(self, key, obj):
        raise NotImplementedError

    def get(self, key, obj):
        raise NotImplementedError

class GiottoMemcache(GiottoCache):
    def __init__(self, host, behavior={}):
        if hasattr(host, 'lower'):
            host = [host]
        kwargs = {'servers': host, 'binary': True}
        if behavior:
            kwargs['behavior'] = behavior
        self.client = pylibmc.Client(**kwargs)

    def set(self, key, obj, expire):
        self.client.set(key, obj, time=expire)

    def get(self, key):
        return self.client.get(key)