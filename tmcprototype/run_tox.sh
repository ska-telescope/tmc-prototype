#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
cd centralnode;
tox -e py37
cd ..
cd cspmasterleafnode
tox -e py37