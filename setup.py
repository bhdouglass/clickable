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

with open('clickable/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

requirements = [
    'cookiecutter',
    'requests',
    'jsonschema',
]

setup(
    name='clickable-ut',
    version=version,
    description='Compile, build, and deploy Ubuntu Touch click packages all from the command line.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Brian Douglass',
    url='https://clickable-ut.dev/',
    project_urls={
        'Documentation': 'https://clickable-ut.dev/en/latest/',
        'Source': 'https://gitlab.com/clickable/clickable',
        'Bug Tracker': 'https://gitlab.com/clickable/clickable/-/issues',
    },
    packages=['clickable'],
    include_package_data=True,
    install_requires=requirements,
    license='GPL3',
    zip_safe=False,
    keywords='click ubuntu touch ubports',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'console_scripts': [
            'clickable = clickable:main',
        ],
    }
)
