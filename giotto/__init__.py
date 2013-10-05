__version__ = '0.11.0'

import importlib
import logging
import os
import sys

class GiottoSettings(object):
    pass

def initialize(module_name=None):
    """
    Build the giotto settings object. This function gets called
    at the very begining of every request cycle.
    """
    import giotto
    from giotto.utils import random_string, switchout_keyvalue
    from django.conf import settings

    setattr(giotto, '_config', GiottoSettings())

    if not module_name:
        # For testing. No settings will be set.
        return

    project_module = importlib.import_module(module_name)
    controllers = importlib.import_module("%s.controllers" % module_name)
    secrets = getattr(project_module.controllers, 'secrets', None)
    machine = getattr(project_module.controllers, 'machine', None)
    config = getattr(project_module.controllers, 'config', None)
    project_path = os.path.dirname(project_module.__file__)

    setattr(giotto._config, 'project_path', project_path)

    if config:
        for item in dir(config):
            setting_value = getattr(secrets, item)
            setattr(giotto._config, item, setting_value)

    if secrets:
        for item in dir(secrets):
            setting_value = getattr(secrets, item)
            setattr(giotto._config, item, setting_value)
    else:
        logging.warning("No secrets.py found")

    if machine:
        for item in dir(machine):
            setting_value = getattr(machine, item)
            setattr(giotto._config, item, setting_value)
    else:
        logging.warning("No machine.py found")

    settings.configure(
        SECRET_KEY=random_string(32),
        DATABASES=get_config('DATABASES'),
        INSTALLED_APPS=(module_name, 'giotto')
    )

    ss = get_config('session_store', None)
    if ss:
        class_ = switchout_keyvalue(ss)
        setattr(giotto._config, "session_store", class_())

    cache_engine = get_config("cache", None)
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