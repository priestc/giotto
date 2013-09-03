__version__ = '0.11.0'

import os
import imp
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def switchout_keyvalue(engine):
    from giotto import keyvalue
    if engine == 'dummy':
        return keyvalue.DummyKeyValue
    if engine == 'locmem':
        return keyvalue.LocMemKeyValue
    if engine == 'database':
        return keyvalue.DatabaseKeyValue
    if engine == 'memcached':
        return keyvalue.MemcacheKeyValue
    if engine == 'redis':
        return keyvalue.RedisKeyValue

def initialize(config=None, secrets=None, machine=None):
    """
    Build the giotto settings object. This function gets called
    at the very begining of every request cycle.
    """
    import giotto
    setattr(giotto, '_config', config)

    if secrets:
        for item in dir(secrets):
            s_value = getattr(secrets, item)
            setattr(giotto._config, item, s_value)

    if machine:
        for item in dir(machine):
            s_value = getattr(machine, item)
            setattr(giotto._config, item, s_value)

    ##################
    # Make a 'mock' module out of settings gleamed from config.py
    # This is done in leiu of having a seperate django settings file
    # for pointing DJANGO_SETTINGS_MODULE to. I18N and L10N are
    # disabled because they apparently don't like our mock
    # settings module method.
    
    giotto_django_bridge = imp.new_module("giotto_django_bridge")
    settings = "%s;%s;USE_L10N = False;USE_I18N = False" % (
        'DATABASES = %s' % str(get_config('DATABASES')),
        'INSTALLED_APPS = ("models")',
    )
    exec settings in giotto_django_bridge.__dict__
    sys.modules["giotto_django_bridge"] = giotto_django_bridge
    os.environ["DJANGO_SETTINGS_MODULE"] = 'giotto_django_bridge'

    ##################

    auth_engine = get_config('auth_session_engine', None)
    if auth_engine:
        class_ =  switchout_keyvalue(auth_engine)
        setattr(giotto._config, "auth_session_engine", class_())

    cache_engine = get_config("cache_engine", None)
    if hasattr(cache_engine, 'lower'):
        # session engine was passed in as string, exchange for engine object.
        class_ = switchout_keyvalue(cache_engine)
        e = class_(host=get_config("cache_host", "localhost"))
        setattr(giotto._config, "cache_engine", e)

def get_config(item, default=None):
    """
    Use this function to get values from the config object.
    """
    import giotto
    return getattr(giotto._config, item, default) or default