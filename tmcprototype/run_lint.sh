#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_lint file...."
python3 -m pip install pylint2junit junitparser; \
python3 -m pip install --index-url https://nexus.engageska-portugal.pt/repository/pypi/simple ska-logging==0.3.0
cd centralnode; \
python3 -m pip install .; \
cd ../../
ls
mkdir -p /build/reports; \
pylint --rcfile=.pylintrc --output-format=parseable tmcprototype | tee /build/reports/linting.stdout; \
pylint --rcfile=.pylintrc --output-format=pylint2junit.JunitReporter tmcprototype > /build/reports/linting.xml;
    

# cd centralnode
# tox -e lint
# cd ../cspmasterleafnode
# tox -e lint
# cd ../cspsubarrayleafnode
# tox -e lint
# cd ../dishleafnode
# tox -e lint
# cd ../sdpmasterleafnode
# tox -e lint
# cd ../sdpsubarrayleafnode
# tox -e lint
# cd ../subarraynode
# tox -e lint
# ls
# python3 -m pip install pylint2junit junitparser; \
# mkdir -p /build/reports; \
# pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR) | tee /build/reports/linting.stdout; \
# pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR) > /build/reports/linting.xml;

