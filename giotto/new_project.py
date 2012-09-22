"""
Makes the directory structure for new projects

{{project}}/
    setup.py
    {{project}}/
        config.py
        controllers/
        views/
        models/

Usage:
    $ giotto new_project
    << interactive >>

    $ giotto new_project --name=project

"""

import os
import jinja2

setup_template = """
from distutils.core import setup

setup(
	name='{{ project }}',
    version='0.0.1',
    description='{{ short_description }}',
    author='{{ author_name }}',
    author_email='{{ author_email }}',
    url='{{ url }}',
    packages=['giotto'],
    license='LICENSE',
    install_requires=['giotto'],
)
"""

settings_template = """
AUTH_STORAGE = 'redis' # 'postgres' | 'mysql' | 'mongodb' | 'oracle'
"""

wsgi_template = """
from giotto.http import make_app
from werkzeug.serving import run_simple
import {{ project }}

app = make_app(blog)
run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
"""

if __name__ == '__main__':
	rendered_setup = jinja2.render(setup_template)
	# place setup.py file
	# create blank directories
	# place config file
	# place wsgi template