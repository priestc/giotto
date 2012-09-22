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
    description='',
    author='',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/giotto',
    packages=['giotto'],
    scripts=['giotto/giotto-commandline.py'],
    license='LICENSE',
    install_requires=['werkzeug', 'distribute'],
)
"""

settings_template = """
AUTH_STORAGE = 'redis' # 'postgres' | 'mysql' | 'mongodb' | 'oracle'
"""

if __name__ == '__main__':
	rendered_setup = jinja2.render(setup_template)
	# place setup.py file
	# create blank directories
	# place config file