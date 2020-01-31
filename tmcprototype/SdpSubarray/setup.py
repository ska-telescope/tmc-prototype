#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the SdpSubarray project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

import os
import sys
from setuptools import setup

setup_dir = os.path.dirname(os.path.abspath(__file__))

# make sure we use latest info from local code
sys.path.insert(0, setup_dir)

readme_filename = os.path.join(setup_dir, 'README.rst')
with open(readme_filename) as file:
    long_description = file.read()

release_filename = os.path.join(setup_dir, 'SdpSubarray', 'release.py')
exec(open(release_filename).read())

pack = ['SdpSubarray']

setup(name=name,
      version=version,
      description='SDP Subarray device',
      packages=pack,
      include_package_data=True,
      test_suite="test",
      entry_points={'console_scripts':['SdpSubarray = SdpSubarray:main']},
      author='apurva.ska',
      author_email='apurva.ska at gmail.com',
      license='GPL',
      long_description=long_description,
      url='www.tango-controls.org',
      platforms="All Platforms",
      install_requires=['pytango==9.3.1', 'mock'],
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
          'pytest-cov',
          'pytest-json-report',
          'pycodestyle',
      ],
      extras_require={
          'dev': ['prospector[with_pyroma]', 'yapf', 'isort']
      }
      )
