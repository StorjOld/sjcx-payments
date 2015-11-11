from setuptools import setup

setup(
    name='sjcx-payments', version='1.0',
    description = 'sjcx rewards calculator',
    author = 'Andrew Kim', author_email='shawn@storj.io',
    url='http://storj.io',
    install_requires=['xlrd', 'requests', 'pymongo']
    tests_require=['coverage', 'coveralls'],
    test_suite='tests',
)

