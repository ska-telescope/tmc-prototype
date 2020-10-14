#!/bin/bash
set -eo pipefail

# export working_dir=../build/reports/tox_report
REPORTS_DIR=reports
# export reports_dir=./$REPORTS_DIR
# echo $reports_dir
# Entering into a bash shell script to run unit-test cases and generating reports
echo "Unit test cases will be executed shortly..."
mkdir -p ./$REPORTS_DIR

# check if build folder is present
echo "Check 1"
# cd ..
ls -l
# cd -


# if [ -d "$working_dir" ]; then rm -rf $working_dir; fi
if [ -d "./$REPORTS_DIR" ]; then rm -rf ./$REPORTS_DIR; fi

# check if build folder is present
echo "Check 2"
# cd ..
ls -l
# cd -

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo +++ Trying tests for $TMC_ELEMENT;
	cd $TMC_ELEMENT;
	tox -e py37
  mv ${TMC_ELEMENT}_coverage ../$REPORTS_DIR/${TMC_ELEMENT}_coverage;
  cd ..
done

# check if build folder is present
echo "Check 3"
# cd ..
ls -l
# cd -

# mv ./tox_report ../build/reports

# cd ../build/reports/tox_report
cd $REPORTS_DIR
echo "Check 4"
ls -l
# Combine coverage reports
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage subarraynodelow_coverage centralnodelow_coverage \
                  mccsmasterleafnode_coverage mccssubarrayleafnode_coverage && coverage xml

# cd ../tox_report && mv coverage.xml ../code-coverage.xml
# cd ../../../tmcprototype
mv coverage.xml code-coverage.xml
echo "Check 5"
ls -l

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
                $REPORTS_DIR/unit-tests.xml
                # ../build/reports/unit-tests.xml
