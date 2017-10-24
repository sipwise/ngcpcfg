#!/usr/bin/env python3

from setuptools import setup
from codecs import open
from os import path

twd = path.abspath(path.dirname(__file__))

with open(path.join(twd, 'README.adoc'), encoding='utf-8') as fd:
    long_description = fd.read()

setup(
    name='network_xls2yml',
    version='0.2.0',
    description='Convert network specifications from XLS spreadsheets to YAML',
    long_description=long_description,
    author='Michael Prokop',
    author_email='mprokop@sipwise.com',
    license='All rights reserved',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Installation/Setup',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='network yaml xls ipaddr vlan',
    py_modules=["network_xls2yml/xls2yml"],
    packages=['network_xls2yml'],
    install_requires=['ruamel.yaml', 'openpyxl'],
    extras_require={'test': ['pytest']},
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'xls2yml=network_xls2yml.xls2yml:cli',
        ],
    },
)
