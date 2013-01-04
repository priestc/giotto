import argparse
import string
import random
import json
import traceback
import re
import unicodedata

from collections import defaultdict
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import class_mapper, ColumnProperty

import giotto

class Mock(object):
    """
    This class creates an object that will replace the error object when no error
    object exists. It allows arbirtary attribute getting without raising an
    attribute error.
    >>> m = Mock()
    >>> m.nothing.empty.made_up.wut.lol
    ''
    >>> bool(m.wut)
    False
    """
    def __getattribute__(self, item):
        return Mock()

    def __str__(self):
        return ''

    def __bool__(self):
        return False

    def __nonzero__(self):
        return False

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
    for k, v in d.items():
        # replace single item lists with just the item.
        if len(v) == 1 and type(v) is list:
            ret[k] = v[0]
        else:
            ret[k] = v
    return ret

def super_accept_to_mimetype(ext):
    if not ext:
        return
    if ext.startswith('.'):
        ext = ext[1:]
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
    if ext == 'css':
        return "text/css"
    if ext == 'irc':
        return 'text/x-irc'


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
                if isinstance(prop, ColumnProperty)]

        def todict(self):
            attrs = self.attribute_names()
            return dict((attr, getattr(self, attr)) for attr in attrs)

    return BetterBase

def htmlize(value):
    """
    Turn any object into a html viewable entity.
    """
    return str(value).replace('<', '&lt;').replace('>', '&gt;')

def htmlize_list(items):
    """
    Turn a python list into an html list.
    """
    out = ["<ul>"]
    for item in items:
        out.append("<li>" + htmlize(item) + "</li>")
    out.append("</ul>")
    return "\n".join(out)

def pre_process_json(obj):
    """
    Preprocess items in a dictionary or list and prepare them to be json serialized.
    """
    if type(obj) is dict:
        new_dict = {}
        for key, value in obj.items():
            new_dict[key] = pre_process_json(value)
        return new_dict

    elif type(obj) is list:
        new_list = []
        for item in obj:
            new_list.append(pre_process_json(item))
        return new_list

    elif hasattr(obj, 'todict'):
        return dict(obj.todict())

    else:
        try:
            json.dumps(obj)
        except TypeError:
            try:
                json.dumps(obj.__dict__)
            except TypeError:
                return str(obj)
            else:
                return obj.__dict__
        else:
            return obj


def render_error_page(code, exc, traceback=''):
    """
    Render the error page
    """
    et = giotto.config.error_template
    if not et:
        return "%s %s\n%s" % (code, str(exc), traceback)
    template = giotto.config.jinja2_env.get_template(et)
    return template.render(
        code=code,
        exception=exc.__class__.__name__,
        message=str(exc),
        traceback=traceback
    )

def slugify(s):
    try:
        s = unicode(s)
    except NameError:
        # python 3
        s = str(s)

    slug = unicodedata.normalize('NFKD', s)
    slug = slug.encode('ascii', 'ignore').lower()
    slug = re.sub(r'[^a-z0-9]+', '-', str(slug)).strip('-')
    slug = re.sub(r'--+', '-', slug)
    return slug

def jsonify(obj):
    def handler(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if hasattr(obj, 'todict'):
            return obj.todict()
        else:
            raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))
    return json.dumps(obj, default=handler)

class FileIterable(object):
    """
    Taken from the webob docs.
    """
    def __init__(self, filename):
        self.filename = filename
    
    def __iter__(self):
        return FileIterator(self.filename)

class FileIterator(object):
    chunk_size = 4096
    
    def __init__(self, filename):
        self.filename = filename
        self.fileobj = open(self.filename, 'rb')
    
    def __iter__(self):
       return self
    
    def next(self):
        chunk = self.fileobj.read(self.chunk_size)
        if not chunk:
            raise StopIteration
        return chunk
    
    __next__ = next # py3 compat









