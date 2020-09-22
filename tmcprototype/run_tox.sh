#!/bin/bash
set -eo pipefail
export working_dir=./build/reports/tox_report
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
mkdir -p tox_report
echo "Check reports if tox_reports already exists...."
ls ./build/reports/

if [ -d "$working_dir" ]; then rm -rf $working_dir; fi
cd centralnode
tox -e py37
mv centralnode_coverage ../tox_report/centralnode_coverage
cd ../cspmasterleafnode
tox -e py37
mv cspmasterleafnode_coverage ../tox_report/cspmasterleafnode_coverage
cd ../cspsubarrayleafnode
tox -e py37
mv cspsubarrayleafnode_coverage ../tox_report/cspsubarrayleafnode_coverage
cd ../dishleafnode
tox -e py37
mv dishleafnode_coverage ../tox_report/dishleafnode_coverage
cd ../sdpmasterleafnode
tox -e py37
mv sdpmasterleafnode_coverage ../tox_report/sdpmasterleafnode_coverage
cd ../sdpsubarrayleafnode
tox -e py37
mv sdpsubarrayleafnode_coverage ../tox_report/sdpsubarrayleafnode_coverage
cd ../subarraynode
tox -e py37
mv subarraynode_coverage ../tox_report/subarraynode_coverage
cd ../
mv ./tox_report ../build/reports
cd ../
cd build/reports
cd tox_report

# # Combine coverage reports
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage && coverage xml
pwd
cd ..
cd ./tox_report && mv coverage.xml ../tox_code-coverage.xml
cd ../../../tmcprototype
echo "In tmcprototype"
pwd
ls

python3 -m pip install junitparser
junitparser merge ./centralnode/build/reports/centralnode-unit-tests.xml \
                ./cspmasterleafnode/build/reports/cspmasterleafnode-unit-tests.xml \
                ./cspsubarrayleafnode/build/reports/cspsubarrayleafnode-unit-tests.xml \
                ./dishleafnode/build/reports/dishleafnode-unit-tests.xml \
                ./sdpmasterleafnode/build/reports/sdpmasterleafnode-unit-tests.xml \
                ./sdpsubarrayleafnode/build/reports/sdpsubarrayleafnode-unit-tests.xml \
                ./subarraynode/build/reports/subarraynode-unit-tests.xml \
                ../build/reports/tox_unit-tests.xml
ls