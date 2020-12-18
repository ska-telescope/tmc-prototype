#!/bin/bash
set -eo pipefail

REPORTS_DIR=../build/reports

# Entering into a bash shell script to run unit-test cases and generating reports
echo "Unit test cases will be executed shortly..."

if [ -d "$REPORTS_DIR" ]; then rm -rf $REPORTS_DIR; fi

mkdir -p $REPORTS_DIR

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo +++ Trying tests for $TMC_ELEMENT;
	cd $TMC_ELEMENT;
	tox -e py37
mv ${TMC_ELEMENT}_coverage ../$REPORTS_DIR;
cd ..
done

# Combine coverage reports
cd $REPORTS_DIR
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage subarraynodelow_coverage centralnodelow_coverage \
                  mccsmasterleafnode_coverage mccssubarrayleafnode_coverage && coverage xml
mv coverage.xml code-coverage.xml
python3 -m pip install junitparser
junitparser merge centralnode-unit-tests.xml \
                  centralnodelow-unit-tests.xml \
                  cspmasterleafnode-unit-tests.xml \
                  cspsubarrayleafnode-unit-tests.xml \
                  dishleafnode-unit-tests.xml \
                  sdpmasterleafnode-unit-tests.xml \
                  sdpsubarrayleafnode-unit-tests.xml \
                  mccsmasterleafnode-unit-tests.xml \
                  mccssubarrayleafnode-unit-tests.xml \
                  subarraynode-unit-tests.xml \
                  subarraynodelow-unit-tests.xml \
                  unit-tests.xml
