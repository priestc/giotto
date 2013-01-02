from setuptools import setup

setup(
	name='giotto',
    version='0.9.15',
    description='Functional Web Framework',
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
    include_package_data=True,
    license='LICENSE',
    install_requires=[
        'werkzeug',
        'irc==5.0.1',
        'jinja2',
        'py-bcrypt',
        'mimeparse',
        'python-magic',
        'sqlalchemy',
    ],
)