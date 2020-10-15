#!/bin/bash
set -eo pipefail

export working_dir=../build/reports/tox_report

# Entering into a bash shell script to run unit-test cases and generating reports
echo "Unit test cases will be executed shortly..."
mkdir -p tox_report
if [ -d "$working_dir" ]; then rm -rf $working_dir; fi

# for path in $(find ./*/test  -type d -name unit); do
# 	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
# 	echo +++ Trying tests for $TMC_ELEMENT;
# 	cd $TMC_ELEMENT;
# 	tox -e py37
#   mv ${TMC_ELEMENT}_coverage ../tox_report/${TMC_ELEMENT}_coverage;
#   cd ..
# done
cd sdpsubarrayleafnode;
tox -e py37
# mv ./tox_report ../build/reports

cd ../build/reports/tox_report
# Combine coverage reports
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage subarraynodelow_coverage centralnodelow_coverage \
                  mccsmasterleafnode_coverage mccssubarrayleafnode_coverage && coverage xml

cd ../tox_report && mv coverage.xml ../code-coverage.xml
cd ../../../tmcprototype

python3 -m pip install junitparser
junitparser merge ./centralnode/build/reports/centralnode-unit-tests.xml \
                 ./centralnodelow/build/reports/centralnodelow-unit-tests.xml \
                ./cspmasterleafnode/build/reports/cspmasterleafnode-unit-tests.xml \
                ./cspsubarrayleafnode/build/reports/cspsubarrayleafnode-unit-tests.xml \
                ./dishleafnode/build/reports/dishleafnode-unit-tests.xml \
                ./sdpmasterleafnode/build/reports/sdpmasterleafnode-unit-tests.xml \
                ./sdpsubarrayleafnode/build/reports/sdpsubarrayleafnode-unit-tests.xml \
                ./mccsmasterleafnode/build/reports/mccsmasterleafnode-unit-tests.xml \
                ./mccssubarrayleafnode/build/reports/mccssubarrayleafnode-unit-tests.xml \
                ./subarraynode/build/reports/subarraynode-unit-tests.xml \
                ./subarraynodelow/build/reports/subarraynodelow-unit-tests.xml \
                ../build/reports/unit-tests.xml
