import six
from giotto import get_config
from django.core.management import call_command

def syncdb():
    """
    Create all the tables for the models that have been added to the manifest.
    """
    call_command('syncdb', traceback=True)

def flush():
    """
    Drop all existing tables in the database, and then recreate them.
    """
    return call_command('flush', traceback=True)