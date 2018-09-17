import re

from setuptools import setup

_version_re = re.compile(r"__version__ = '(.*)'")

with open('src/fashionable/__init__.py') as f:
    version = str(_version_re.search(f.read()).group(1))

setup(
    name='fashionable',
    version=version,
    packages=['fashionable'],
    package_dir={'': 'src'},
    url='https://github.com/mon4ter/fashionable',
    license='MIT',
    author='Dmitry Galkin',
    author_email='mon4ter@gmail.com',
    description='Decorate your project with some fashionable supermodels'
)
