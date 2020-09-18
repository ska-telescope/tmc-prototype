#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
mkdir tox_report
cd centralnode;
tox -e py37
cd ../cspmasterleafnode
tox -e py37
cd ../cspsubarrayleafnode
tox -e py37
cd ../dishleafnode
tox -e py37
cd ../sdpmasterleafnode
tox -e py37
cd ../sdpsubarrayleafnode
tox -e py37
cd ../subarraynode
tox -e py37
cd ..

mv build/reports/centralnode-code-coverage.xml tox_report/centralnode-code-coverage.xml
mv build/reports/cspmasterleafnode-code-coverage.xml tox_report/cspmasterleafnode-code-coverage.xml
mv build/reports/cspsubarrayleafnode-code-coverage.xml tox_report/cspsubarrayleafnode-code-coverage.xml
mv build/reports/dishleafnode-code-coverage.xml tox_report/dishleafnode-code-coverage.xml
mv build/reports/sdpmasterleafnode-code-coverage.xml tox_report/sdpmasterleafnode-code-coverage.xml
mv build/reports/sdpsubarrayleafnode-code-coverage.xml tox_report/sdpsubarrayleafnode-code-coverage.xml
mv build/reports/subarraynode-code-coverage.xml tox_report/subarraynode-code-coverage.xml