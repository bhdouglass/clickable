#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open('README.md').read()

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('clickable.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

requirements = [
    "cookiecutter",
]

test_requirements = [
    "ipdb",
]

setup(
    name='clickable',
    version=version,
    description='Compile, build, and deploy Ubuntu Touch click packages all'
                'from the command line.',
    long_description=readme,
    author='Brian Douglass',
    url='https://github.com/bhdouglass/clickable',
    py_modules=['clickable'],
    include_package_data=True,
    install_requires=requirements,
    license="GPL3",
    zip_safe=False,
    keywords='click ubuntu touch ubports',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        "console_scripts": [
            "clickable = clickable:main",
        ],
    }
)
