from setuptools import setup

setup(
	name='giotto',
    version='0.1.0',
    description='MVC Application Framework',
    long_description=open('README.md').read(),
    author='Chris Priest',
    author_email='cp368202@ohiou.edu',
    url='https://github.com/priestc/giotto',
    packages=[
        'giotto',
        'giotto.controllers',
        'giotto.contrib.auth',
        'giotto.contrib.static',
        'giotto.views'
    ],
    scripts=['giotto/giotto_project'],
    license='LICENSE',
    install_requires=['werkzeug', 'python-magic', 'jinja2', 'py-bcrypt', 'decorator'],
)