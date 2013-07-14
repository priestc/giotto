from setuptools import setup
import sys

REQUIRES = [
    'webob==1.2.3',
    'six==1.2.0',
    'irc==5.0.1',
    'jinja2==2.6',
    'py-bcrypt==0.2',
    'python-mimeparse==0.1.4',
    'sqlalchemy==0.8.2',
]

print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
if sys.version_info < (2, 7):
    print("2.6-2.6-2.6-2.6-2.6-2.6-2.6-2.6-2.6-2.6-2.6-2.6-2.6-2.6")
    REQUIRES.append('ordereddict')

setup(
    name='giotto',
    version='0.11.0',
    description='Web development simplified. An MVC framework supporting Python 3.',
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
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=REQUIRES,
)