#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CentralNode project
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

release_filename = os.path.join(setup_dir, 'CentralNode', 'release.py')
exec(open(release_filename).read())

pack = ['CentralNode']

setup(name=name,
      version=version,
      description='Central Node is a coordinator of the complete M&C system.',
      packages=pack,
      include_package_data=True,
      test_suite="test",
      entry_points={'console_scripts':['CentralNode = CentralNode:main']},
      author='apurva.ska',
      author_email='apurva.ska at gmail.com',
      license='GPL',
      long_description=long_description,
      url='www.tango-controls.org',
      platforms="All Platforms"
      )
