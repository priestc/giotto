from collections import defaultdict
import datetime
import pickle

from sqlalchemy import Column, String, DateTime

try:
    import pylibmc
except ImportError:
    pylibmc = None

try:
    import redis
except ImportError:
    redis = None

DBKeyValue = None

class GiottoKeyValue(object):
    """
    Baseclass for all KeyValue object. This exists to demonstrate the API for
    KeyValue subclasses.
    """
    def set(self, key, obj):
        raise NotImplementedError

    def get(self, key, obj):
        raise NotImplementedError

class DatabaseKeyValue(GiottoKeyValue):
    def __init__(self, base, session):
        """
        Since we can't get the base class by importing it (base class defined in
        the config file, which is where this class is initialized). The base
        class must be passed in via this constructor. The SQLAlchemy model
        is then passed back into the mosule scope where it can be used
        by the DatabaseKeyValue backend.
        """
        if not base:
            return
        class _DBKeyValue(base):
            __tablename__ = 'giotto_keyvalue'
            key = Column(String, primary_key=True)
            value = Column(String)
            expires = Column(DateTime)

            @classmethod
            def set(cls, key, obj, expire):
                when_expire = datetime.datetime.now() + datetime.timedelta(seconds=expire)
                new = cls(key=key, value=pickle.dumps(obj), expires=when_expire)
                session.merge(new)
                session.commit()

            @classmethod
            def get(cls, key):
                value = session.query(cls)\
                               .filter_by(key=key)\
                               .filter(cls.expires > datetime.datetime.now())\
                               .first()
                
                if value:
                    return pickle.loads(str(value.value))
                return None

        global DBKeyValue
        DBKeyValue = _DBKeyValue

    def get(self, key):
        return DBKeyValue.get(key)

    def set(self, key, obj, expire):
        return DBKeyValue.set(key, obj, expire)

locmem = {}
class LocMemKeyValue(GiottoKeyValue):
    """
    KeyValue backend that stores everything in a python dict.
    """
    def get(self, key):
        if key not in locmem:
            return None

        result = locmem[key]
        expire = result[1]
        obj = result[0]

        if datetime.datetime.now() < expire:
            return obj

        del locmem[key]
        return None # obj has expired.

    def set(self, key, obj, expire):
        when_expire = datetime.datetime.now() + datetime.timedelta(seconds=expire)
        locmem[key] = (obj, when_expire)


class MemcacheKeyValue(GiottoKeyValue):
    def __init__(self, host=['localhost'], behavior={}):
        if not pylibmc:
            msg = 'pylibmc not installed! install with: pip install pylibmc'
            raise ImportError(msg)
        if hasattr(host, 'lower'):
            host = [host]
        kwargs = {'servers': host, 'binary': True}
        if behavior:
            kwargs['behavior'] = behavior
        self.client = pylibmc.Client(**kwargs)

    def set(self, key, obj, expire):
        self.client.set(str(key), obj, time=expire)

    def get(self, key):
        return self.client.get(str(key))

class RedisKeyValue(GiottoKeyValue):
    def __init__(self, host='localhost', port=6379, db=0):
        if not redis:
            msg = 'redis python wrapper not installed! install with: pip install redis'
            raise ImportError(msg)
        self.redis = redis.StrictRedis(host=host, port=port, db=db)

    def set(self, key, obj, expire):
        self.redis.setex(key, expire, pickle.dumps(obj))

    def get(self, key):
        pickled_value = self.redis.get(key)
        if pickled_value is None:
            return None
        return pickle.loads(pickled_value)

class DummyKeyValue(GiottoKeyValue):
    """
    Cache that does not save nor return a hit ever. Used as a placeholder.
    """
    def set(self, key, obj, expire):
        return None

    def get(self, key):
        return None