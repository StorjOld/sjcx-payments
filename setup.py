#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='sjcx-payments', version='1.0',
    description = 'sjcx rewards calculator',
    author = 'Andrew Kim',
    url='http://storj.io',
    install_requires=['xlrd', 'requests', 'pymongo'],
    tests_require=['coverage', 'coveralls'],
    test_suite='tests',
)

