#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CentralNodeLow project
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

release_filename = os.path.join(setup_dir, 'src', 'centralnodelow', 'release.py')
exec(open(release_filename).read())

setup(name=name,
      version=version,
      description='Central Node is a coordinator of the complete M&C system.',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      include_package_data=True,
      test_suite="test",
      entry_points={'console_scripts': ['CentralNodeLowDS=centralnodelow.central_node:main']},
      author='apurva.ska',
      author_email='apurva.ska at gmail.com',
      license='BSD-3-Clause',
      long_description=long_description,
      url='www.tango-controls.org',
      platforms="All Platforms",
      install_requires=['pytango==9.3.2', 'mock', 'ska_logging==0.3.0', 'lmcbaseclasses==0.6.5'],
      # test_suite='test',
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
      ],
      extras_require={
          'dev': ['prospector[with_pyroma]', 'yapf', 'isort']
      }
      )
