#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
#mkdir tox_report
#mkdir reports
cd centralnode;
tox -e py37
mv centralnode_coverage ../tox_report/centralnode_coverage
cd build
echo "In build..."
ls
cd reports
echo "In reports..."
ls

# cd ../cspmasterleafnode
# tox -e py37
# mv cspmasterleafnode_coverage ../tox_report/cspmasterleafnode_coverage
# cd ../cspsubarrayleafnode
# tox -e py37
# mv cspsubarrayleafnode_coverage ../tox_report/cspsubarrayleafnode_coverage
# cd ../dishleafnode
# tox -e py37
# mv dishleafnode_coverage ../tox_report/dishleafnode_coverage
# cd ../sdpmasterleafnode
# tox -e py37
# mv sdpmasterleafnode_coverage ../tox_report/sdpmasterleafnode_coverage
# cd ../sdpsubarrayleafnode
# tox -e py37
# mv sdpsubarrayleafnode_coverage ../tox_report/sdpsubarrayleafnode_coverage
# cd ../subarraynode
# tox -e py37
# mv subarraynode_coverage ../tox_report/subarraynode_coverage
echo "In tox file...."
cd ../tox_report
ls

# # Combine coverage reports
# coverage combine centralnode_coverage cspmasterleafnode_coverage \
#                   cspsubarrayleafnode_coverage dishleafnode_coverage \
#                   sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
#                   subarraynode_coverage && coverage xml
# cd ..
# cd ./tox_report && mv coverage.xml ../reports/tox_code-coverage.xml
# cd ..
# pwd
# python3 -m pip install junitparser
# junitparser merge ./centralnode/build/reports/centralnode-unit-tests.xml \
#                 ./cspmasterleafnode/build/reports/cspmasterleafnode-unit-tests.xml \
#                 ./cspsubarrayleafnode/build/reports/cspsubarrayleafnode-unit-tests.xml \
#                 ./dishleafnode/build/reports/dishleafnode-unit-tests.xml \
#                 ./sdpmasterleafnode/build/reports/sdpmasterleafnode-unit-tests.xml \
#                 ./sdpsubarrayleafnode/build/reports/sdpsubarrayleafnode-unit-tests.xml \
#                 ./subarraynode/build/reports/subarraynode-unit-tests.xml \
#                 ./reports/tox_unit-tests.xml
# cd reports
# ls