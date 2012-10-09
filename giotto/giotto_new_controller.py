"""
Makes a file for invoking a giotto project for a given controller

Usage:
    $ giotto new_controller [--http] [--cmd]
"""

import sys
import jinja2

cmd = "--cmd" in sys.argv
http = "--http" in sys.argv

wsgi_template = """
from giotto import GiottoProgram
from giotto.core import itersubclasses
from giotto.http import make_app
from werkzeug.serving import run_simple

class HelloWorld(GiottoProgram):
    name = "hello_world"
    controller = 'http-get'
    view = TEXT("Hello {{obj}}")

################### generated code below

import sys
programs = list(itersubclasses(GiottoProgram))
controller = sys.argv[1]
"""

if http:
    template = template + \
"""
if controller == 'http':
    app = make_app(programs)
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
"""

if cmd:
    template = template + \
"""
if controller == 'cmd':
    pass

"""

if __name__ == '__main__':
    
	rendered = jinja2.render(template)
    f = open('giotto', 'w')
    r.write(rendered)
    f.close()