__version__ = '0.11.0'

import importlib
import os
import imp
import sys
import logging

def initialize(module_name):
    """
    Build the giotto settings object. This function gets called
    at the very begining of every request cycle.
    """
    import giotto
    setattr(giotto, '_config', config)

    secrets = importlib.import_module("%s.secrets" % module_name)
    machine = importlib.import_module("%s.machine" % module_name)
    config = importlib.import_module("%s.config" % module_name)

    if secrets:
        for item in dir(secrets):
            s_value = getattr(secrets, item)
            setattr(giotto._config, item, s_value)
    else:
        logging.warning("No secrets.py found")

    if machine:
        for item in dir(machine):
            s_value = getattr(machine, item)
            setattr(giotto._config, item, s_value)
    else:
        logging.warning("No machine.py found")

    from giotto.utils import random_string, switchout_keyvalue
    from django.conf import settings
    settings.configure(
        SECRET_KEY=random_string(32),
        DATABASES=get_config('DATABASES'),
        INSTALLED_APPS=(module_name, 'giotto')
    )

    auth_engine = get_config('auth_session_engine', None)
    if auth_engine:
        class_ = switchout_keyvalue(auth_engine)
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