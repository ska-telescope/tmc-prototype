#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SubarrayNodeLow project
#
#
#
# Distributed under the terms of the BSD-3-Clause license.
# See LICENSE.txt for more info.

import os
import sys
from setuptools import setup, find_packages

setup_dir = os.path.dirname(os.path.abspath(__file__))

# make sure we use latest info from local code
sys.path.insert(0, setup_dir)

readme_filename = os.path.join(setup_dir, 'README.rst')
with open(readme_filename) as file:
    long_description = file.read()

release_filename = os.path.join(setup_dir, 'src', 'subarraynodelow', 'release.py')
exec(open(release_filename).read())

setup(
    name=name,
    version=version,
    description='Provides the monitoring and control interface for SKA Low required by users as well as \n'
                'other TM Components (such as OET, Central Node) for a Subarray.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={'console_scripts':['SubarrayNodeLowDS = subarraynodelow.subarray_node_low:main']},
    author='Team NCRA',
    author_email='telmgt-internal@googlegroups.com',
    license='BSD-3-Clause',
    long_description=long_description,
    url='https://www.skatelescope.org',
    platforms="Linux",
    install_requires=['pytango==9.3.2', 'mock', 'ska_logging==0.3.0', 'lmcbaseclasses==0.7.2', 'skatmccommon==0.1.2+b01374cf'],
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'recommonmark'
    ],
    tests_require=[
        'pytest',
        'coverage',
        'pytest-json-report',
        'pycodestyle',
    ],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'yapf', 'isort']
    }
    )