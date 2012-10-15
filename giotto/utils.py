import argparse
from collections import defaultdict

def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>> 
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """
    
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub

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

def parse_controller_args(argv):
    """
    Parse the commandline argument for the concrete controller.
    """
    parser = argparse.ArgumentParser(description='Giotto Concrete Controller')
    parser.add_argument('--http', action='store_true', help='Add the HTTP controller')
    parser.add_argument('--irc', action='store_true', help='Add the IRC controller')
    parser.add_argument('--cmd', help='Add the command line controller', nargs='+')
    parser.add_argument('--model-mock', action='store_true', help='Run with models mocked')
    return parser.parse_args(argv[1:])










