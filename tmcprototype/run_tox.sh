#!/bin/bash
set -eo pipefail

# export working_dir=../build/reports/tox_report
REPORTS_DIR=../build/reports
# export reports_dir=./$REPORTS_DIR
# echo $reports_dir
# Entering into a bash shell script to run unit-test cases and generating reports
echo "Unit test cases will be executed shortly..."

# check if build folder is present
echo "Check 1"
# cd ..
ls -l
# cd -

if [ -d "$REPORTS_DIR" ]; then rm -rf $REPORTS_DIR; fi

# check if build folder is present
echo "Check 2"
# cd ..
ls -l
# cd -

mkdir -p $REPORTS_DIR
echo "Check 3"
ls -l

# reports_dir_path := $(abspath $REPORTS_DIR)
# export REPORTS_DIR_PATH=$reports_dir_path

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo +++ Trying tests for $TMC_ELEMENT;
	cd $TMC_ELEMENT;
	tox -e py37
  mv ${TMC_ELEMENT}_coverage ../$REPORTS_DIR;
  cd ..
done

# check if build folder is present
echo "Check 4"
cd $REPORTS_DIR
ls -l 
# cd -

# mv ./tox_report ../build/reports

# cd ../build/reports/tox_report
# cd $REPORTS_DIR
# echo "Check 5"
# ls -l
# Combine coverage reports
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage subarraynodelow_coverage centralnodelow_coverage \
                  mccsmasterleafnode_coverage mccssubarrayleafnode_coverage && coverage xml

# cd ../tox_report && mv coverage.xml ../code-coverage.xml
# cd ../../../tmcprototype
mv coverage.xml code-coverage.xml
echo "Check 6"
ls -l

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
                  # dishmaster-unit-tests.xml \
                # ../build/reports/unit-tests.xml
