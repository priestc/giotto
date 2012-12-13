import argparse
import string
import random
from collections import defaultdict
from sqlalchemy.ext.declarative import declarative_base, declared_attr

import giotto

class Mock(object):
    """
    This class creates an object that will replace the error object when no error
    object exists. It allows arbirtary attribute getting without raising an
    attribute error.
    >>> m = Mock()
    >>> m.nothing.empty.made_up.wut.lol
    ''
    """
    def __getattribute__(self, item):
        return Mock()

    def __str__(self):
        return ''

def parse_kwargs(kwargs):
    """
    Convert a list of kwargs into a dictionary. Duplicates of the same keyword
    get added to an list within the dictionary.

    >>> parse_kwargs(['--var1=1', '--var2=2', '--var1=3']
    {'var1': [1, 3], 'var2': 2}
    """
    
    d = defaultdict(list)
    for k, v in ((k.lstrip('-'), v) for k,v in (a.split('=') for a in kwargs)):
        d[k].append(v)

    ret = {}
    for k, v in d.iteritems():
        # replace single item lists with just the item.
        if len(v) == 1 and type(v) is list:
            ret[k] = v[0]
        else:
            ret[k] = v
    return ret

def super_accept_to_mimetype(ext):
    if ext in ('jpeg', 'jpg'):
        return 'image/jpeg'
    if ext == 'gif':
        return 'image/gif'
    if ext == 'txt':
        return 'text/plain'
    if ext in ('html', 'htm'):
        return 'text/html'
    if ext == 'json':
        return 'application/json'

def initialize_giotto(config):
    setattr(giotto, 'config', config)

def random_string(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(n))

def better_base():
    """
    Return a better SQLAlchemy Base class, for making things a little easier to
    work with.
    """
    Base = declarative_base()
    class BetterBase(Base):
        __abstract__ = True

        @declared_attr
        def __tablename__(cls):
            return "giotto_" + cls.__name__.lower()

        @classmethod
        def attribute_names(cls):
            return [prop.key for prop in class_mapper(cls).iterate_properties
                if isinstance(prop, sqlalchemy.orm.ColumnProperty)]

        def todict(self):
            attrs = self.attribute_names()
            return [(x, getattr(self, attr)) for attr in attrs]

    return BetterBase








