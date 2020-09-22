#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_lint file...."
python3 -m pip install pylint2junit junitparser; \
python3 -m pip install --index-url https://nexus.engageska-portugal.pt/repository/pypi/simple ska-logging==0.3.0 lmcbaseclasses==0.6.5 cdm-shared-library==2.0.0 ska-telescope-model==0.1.4 
cd centralnode; \
python3 -m pip install .; \
cd ../cspmasterleafnode
python3 -m pip install .; \
cd ../cspsubarrayleafnode
python3 -m pip install .; \
cd ../dishleafnode
python3 -m pip install .; \
cd ../sdpmasterleafnode
python3 -m pip install .; \
cd ../sdpsubarrayleafnode
python3 -m pip install .; \
cd ../subarraynode
python3 -m pip install .; \

cd ../../
ls
mkdir -p ./build/reports; \
pylint --rcfile=.pylintrc --output-format=parseable tmcprototype | tee ./build/reports/linting.stdout; \
pylint --rcfile=.pylintrc --output-format=pylint2junit.JunitReporter tmcprototype > ./build/reports/linting.xml;
    

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

