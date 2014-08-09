# encoding: utf-8
from setuptools import setup, find_packages

setup(
    name='ansible-inventory',
    version='0.1.0',
    packages=find_packages(exclude=('test',)),
    license='BSD License',
    description='Configurable Ansible inventory generation',
    url='https://github.com/gaqzi/ansible-inventory/',
    author='Björn Andersson',
    author_email='ba@sanitarium.se',

    install_requires=(
        'dopy>=0.2.3',
    ),
    tests_require=(
        'pytest',
        'pytest-xdist',
        'mock',
    ),
)
