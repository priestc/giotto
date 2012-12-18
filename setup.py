from setuptools import setup

setup(
	name='giotto',
    version='0.9.8',
    description='MVC Application Framework',
    long_description=open('README.rst').read(),
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/giotto',
    packages=[
        'giotto',
        'giotto.controllers',
        'giotto.programs',
        'giotto.contrib',
        'giotto.contrib.auth',
        'giotto.contrib.static',
        'giotto.views'
    ],
    scripts=['bin/giotto'],
    license='LICENSE',
    install_requires=[
        'werkzeug',
        'irc',
        'jinja2',
        'py-bcrypt',
        'mimeparse',
        'python-magic',
        'sqlalchemy',
    ],
)