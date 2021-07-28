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
coverage combine ska-tmc-cspmasterleafnode-mid_coverage dishmaster_coverage \
                  ska-tmc-cspsubarrayleafnode-mid_coverage dishleafnode_coverage \
                  ska-tmc-sdpmasterleafnode-mid_coverage ska-tmc-sdpsubarrayleafnode-mid_coverage \
                  ska-tmc-subarraynode-low_coverage ska-tmc-centralnode-low_coverage \
                  ska-tmc-mccsmasterleafnode-low_coverage ska-tmc-mccssubarrayleafnode-low_coverage && coverage xml
mv coverage.xml code-coverage.xml
python3 -m pip install junitparser
junitparser merge dishmaster-unit-tests.xml \
                  ska-tmc-centralnode-low-unit-tests.xml \
                  ska-tmc-cspmasterleafnode-mid-unit-tests.xml \
                  ska-tmc-cspsubarrayleafnode-mid-unit-tests.xml \
                  dishleafnode-unit-tests.xml \
                  ska-tmc-sdpmasterleafnode-mid-unit-tests.xml \
                  ska-tmc-sdpsubarrayleafnode-mid-unit-tests.xml \
                  ska-tmc-mccsmasterleafnode-low-unit-tests.xml \
                  ska-tmc-mccssubarrayleafnode-low-unit-tests.xml \
                  ska-tmc-subarraynode-low-unit-tests.xml \
                  unit-tests.xml
