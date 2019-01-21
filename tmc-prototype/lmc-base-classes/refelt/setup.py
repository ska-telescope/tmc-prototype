#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the RefA project
#
#
#

import os
import sys
from setuptools import setup, find_packages

setup_dir = os.path.dirname(os.path.abspath(__file__))

# make sure we use latest info from local code
sys.path.insert(0, setup_dir)

readme_filename = os.path.join(setup_dir, 'README.md')
with open(readme_filename) as file:
    long_description = file.read()

release_filename = os.path.join(setup_dir, 'release.py')
exec(open(release_filename).read())

setup(name=name,
      version=version,
      description='An SKA Refence Element (Ref)',
      author="SKA Team",
      packages=find_packages(),  #pack
      include_package_data=True,
      entry_points={'console_scripts':[
          'SvrRefMaster = refelt.RefMaster:main',
          'SvrRefA = refelt.RefA:main',
          'SvrRefAchild = refelt.RefAchild:main',
          'SvrRefB = refelt.RefB:main',
          'SvrRefBchild = refelt.RefBchild:main',
          'SvrRack = refelt.Rack:main',
          'SvrServer = refelt.Server:main',
          'SvrSwitch = refelt.Switch:main',
          'SvrPDU = refelt.PDU:main',
          'SvrFileLogger = refelt.FileLogger:main',
          'SvrRefTelState = refelt.RefTelState:main',
          'SvrRefAlarmHandler = refelt.RefAlarmHandler:main',
          'SvrRefSubarray = refelt.RefSubarray:main',
          'SvrRefCapabilityA = refelt.RefCapabilityA:main',
          'SvrRefCapabilityB = refelt.RefCapabilityB:main',
          'SvrRefCapabilityC = refelt.RefCapabilityC:main',
          'SvrRefCapabilityD = refelt.RefCapabilityD:main',
          ]},
      url='https://www.skatelescope.org/',
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: Other/Proprietary License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Scientific/Engineering :: Astronomy"],
      platforms="All Platforms",
      setup_requires=[],
      install_requires=[],
      tests_require=[
          "nose",
          "coverage",
          "nosexcover",
          "unittest2"
      ],
      keywords="generic element ref elt lmc ska",
      test_suite="nose.collector",
      zip_safe=False)
