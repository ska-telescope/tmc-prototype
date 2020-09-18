#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
cd centralnode;
tox -e py37
cd ../cspmasterleafnode
tox -e py37
cd ../cspsubarrayleafnode
tox -e py37
cd ../dishleafnode
tox -e py37