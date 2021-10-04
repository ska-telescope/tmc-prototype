#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of the CspSubarraySimulator project
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

readme_filename = os.path.join(setup_dir, "README.rst")
with open(readme_filename) as file:
    long_description = file.read()

setup(
    name= "simulators",
    version= "0.0.0",
    description="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "cspsubarraysimulator": [
            "csp_subarray_SimDD.json",
            "CspSubarray.fgo",
        ],
        "sdpsubarraysimulator": [
            "sdp_subarray_SimDD.json",
            "SdpSubarray.fgo",
        ],
        "cspmastersimulator": [
            "csp_master_SimDD.json",
            "CspMaster.fgo",
        ],
        "sdpmastersimulator": [
            "sdp_master_SimDD.json",
            "SdpMaster.fgo",
        ]
    },
    entry_points={
        "console_scripts": [
            "CspSubarraySimulatorDS=cspsubarraysimulator.csp_subarray:main",
            "SdpSubarraySimulatorDS=sdpsubarraysimulator.sdp_subarray:main",
            "CspMasterSimulatorDS=cspmastersimulator.csp_master:main",
            "SdpMasterSimulatorDS=sdpmastersimulator.sdp_master:main",
        ]
        
    },
    author="Team NCRA",
    author_email="telmgt-internal@googlegroups.com",
    license="BSD-3-Clause",
    long_description=long_description,
    url="https://www.skaobservatory.org",
    platforms="Linux",
    install_requires=["pytango==9.3.3"],
    setup_requires=["pytest-runner", "sphinx", "recommonmark"],
    tests_require=[
        "pytest",
        "coverage",
        "pytest-json-report",
        "pycodestyle",
    ],
    extras_require={"dev": ["prospector[with_pyroma]", "yapf", "isort"]},
)
