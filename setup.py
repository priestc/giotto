from setuptools import setup

setup(
	name='giotto',
    version='0.9.16',
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
        'werkzeug==0.8.3',
        'irc==5.0.1',
        'jinja2==2.6',
        'py-bcrypt==0.2',
        'mimeparse==0.1.3',
        'python-magic==0.4.3',
        'sqlalchemy==0.7.9',
    ],
)