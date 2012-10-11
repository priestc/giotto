from setuptools import setup

setup(
	name='giotto',
    version='0.0.2',
    description='MVC microframework',
    long_description=open('README.md').read(),
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/giotto',
    packages=['giotto'],
    scripts=['giotto/giotto_controller'],
    license='LICENSE',
    install_requires=['werkzeug', 'jinja2', 'py-bcrypt', 'decorator'],
)