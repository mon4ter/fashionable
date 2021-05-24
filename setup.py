from re import search

from setuptools import setup

with open('src/fashionable/__init__.py') as f:
    version = str(search(r"__version__ = '(.*)'", f.read()).group(1))

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name='fashionable',
    version=version,
    packages=['fashionable', 'fashionable.decorator'],
    package_dir={'': 'src'},
    setup_requires=[
        "pytest-runner >= 5.2, < 5.3; python_version < '3.6'",
        "pytest-runner >= 5.3, < 5.4; python_version >= '3.6'",
    ],
    tests_require=[
        "pytest >= 6.1, < 6.2; python_version < '3.6'",
        "pytest >= 6.2, < 6.3; python_version >= '3.6'",
        "pytest-asyncio >= 0.14, < 1.15; python_version < '3.6'",
        "pytest-asyncio >= 0.15, < 1.16; python_version >= '3.6'",
        "pytest-cov >= 2.12, < 2.13",
    ],
    url='https://github.com/mon4ter/fashionable',
    license='MIT',
    author='Dmitry Galkin',
    author_email='mon4ter@gmail.com',
    description='Decorate your project with some fashionable supermodels',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
