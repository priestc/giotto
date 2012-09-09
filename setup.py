from setuptools import setup, find_packages

setup(
	name='giotto',
    version='0.0.1',
    description='Python Distribution Utilities',
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/giotto',
    packages=['giotto'],
    install_requires=['werkzeug'],
)