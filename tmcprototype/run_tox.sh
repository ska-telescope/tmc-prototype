#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
mkdir tox_report
cd centralnode;
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
cd ../tox_report
ls

# Combine coverage reports
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage && coverage xml
cd ..
pwd
mv tox_report/coverage.xml build/reports/tox_code-coverage.xml
pwd
ls