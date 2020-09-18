#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
python3 -m pip install pytest-forked mock numpy==1.17.2
python3 -m pip install --index-url https://nexus.engageska-portugal.pt/repository/pypi/simple ska-logging==0.3.0 \
lmcbaseclasses==0.6.5 cdm-shared-library==2.0.0 ska-telescope-model==0.1.4 pytango>=9.3.2 jsonschema>=3.2.0 \
marshmallow fire
cd centralnode;
tox -e py37
#cd ..
#cd cspmasterleafnode
#tox -e py37