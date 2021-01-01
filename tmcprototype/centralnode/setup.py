#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
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

release_filename = os.path.join(setup_dir, 'src', 'centralnode', 'release.py')
exec(open(release_filename).read())

setup(name=name,
      version=version,
      description='Central Node is a coordinator of the complete M&C system.',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      include_package_data=True,
      test_suite="test",
      entry_points={'console_scripts': ['CentralNodeDS=centralnode.central_node:main']},
      author='Team NCRA',
      author_email='telmgt-internal@googlegroups.com',
      license='BSD-3-Clause',
      long_description=long_description,
      url='https://www.skatelescope.org',
      platforms="Linux",
      install_requires=['pytango==9.3.2', 'mock', 'katpoint', 'ska_logging==0.3.0', 'lmcbaseclasses==0.7.2',
                        'skatmccommon==0.1.2+b01374cf'],
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
          'pytest-forked',
          'numpy',
      ],
      extras_require={
          'dev': ['prospector[with_pyroma]', 'yapf', 'isort']
      }
      )
