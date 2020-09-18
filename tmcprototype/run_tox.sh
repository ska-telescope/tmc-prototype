#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
mkdir tox_report
cd centralnode;
tox -e py37
mv build/reports/centralnode-code-coverage.xml ../tox_report/centralnode-code-coverage.xml
cd ../cspmasterleafnode
tox -e py37
mv build/reports/cspmasterleafnode-code-coverage.xml ../tox_report/cspmasterleafnode-code-coverage.xml
cd ../cspsubarrayleafnode
tox -e py37
mv build/reports/cspsubarrayleafnode-code-coverage.xml ../tox_report/cspsubarrayleafnode-code-coverage.xml
cd ../dishleafnode
tox -e py37
mv build/reports/dishleafnode-code-coverage.xml ../tox_report/dishleafnode-code-coverage.xml
cd ../sdpmasterleafnode
tox -e py37
mv build/reports/sdpmasterleafnode-code-coverage.xml ../tox_report/sdpmasterleafnode-code-coverage.xml
cd ../sdpsubarrayleafnode
tox -e py37
mv build/reports/sdpsubarrayleafnode-code-coverage.xml ../tox_report/sdpsubarrayleafnode-code-coverage.xml
cd ../subarraynode
tox -e py37
mv build/reports/subarraynode-code-coverage.xml ../tox_report/subarraynode-code-coverage.xml
cd ../tox_report
ls