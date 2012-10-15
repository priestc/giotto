import pickle
try:
    import pylibmc
except ImportError:
    pylibmc = None

try:
    import redis
except ImportError:
    redis = None

class GiottoCache(object):
    def set(self, key, obj):
        raise NotImplementedError

    def get(self, key, obj):
        raise NotImplementedError

class CacheWithMemcache(GiottoCache):
    def __init__(self, host=['localhost'], behavior={}):
        if not pylibmc:
            raise ImportError('pylibmc not installed! install with: pip install pylibmc')
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

class CacheWithRedis(GiottoCache):
    def __init__(self, host='localhost', port=6379, db=0):
        if not redis:
            raise ImportError('redis python wrapper not installed! install with: pip install redis')
        self.redis = redis.StrictRedis(host=host, port=port, db=db)

    def set(self, key, obj, expire):
        self.redis.setex(key, expire, pickel.dumps(obj))

    def get(self, key):
        pickled_value = self.redis.get(key)
        if pickled_value is None:
            return None
        return pickle.loads(pickled_value)