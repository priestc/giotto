from setuptools import setup, find_packages
import sys

REQUIRES = [
    'webob==1.2.3',
    'six==1.2.0',
    'irc==5.0.1',
    'jinja2==2.6',
    'py-bcrypt==0.4',
    'python-mimeparse==0.1.4',
    'django==1.5.4',
    'argh==0.23.3',
    'requests==1.2.3'
]

if sys.version_info < (2, 7):
    REQUIRES.append('ordereddict')
    REQUIRES.append('importlib')

setup(
    name='giotto',
    version='0.11.0',
    description='Web development simplified. An MVC framework supporting Python 3.',
    long_description=open('README.rst').read(),
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/giotto',
    packages=find_packages(),
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