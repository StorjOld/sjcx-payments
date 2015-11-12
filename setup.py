import os
from setuptools import setup

setup(
    name='sjcx-payments', version='1.0',
    description = 'sjcx rewards calculator',
    author = 'Andrew Kim',
    url='http://storj.io',
    dependency_links=[],
    install_requires=open("requirements.txt").readlines(),
    tests_require=open("test_requirements.txt").readlines(),
    test_suite='tests',
)

