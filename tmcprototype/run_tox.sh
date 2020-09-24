#!/bin/bash
set -eo pipefail

export working_dir=../build/reports/tox_report

#ls ../build/reports/  <- gives error sometimes: No such file or directory
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
mkdir -p tox_report
if [ -d "$working_dir" ]; then rm -rf $working_dir; fi

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo +++ Trying tests for $TMC_ELEMENT;
	cd $TMC_ELEMENT;
	tox -e py37
  mv ${TMC_ELEMENT}_coverage ../tox_report/${TMC_ELEMENT}_coverage;
  cd ..
done
mv ./tox_report ../build/reports

cd ../build/reports/tox_report
# # # Combine coverage reports
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage && coverage xml

cd ../tox_report && mv coverage.xml ../tox_code-coverage.xml
cd ../../../tmcprototype

python3 -m pip install junitparser
junitparser merge ./centralnode/build/reports/centralnode-unit-tests.xml \
                ./cspmasterleafnode/build/reports/cspmasterleafnode-unit-tests.xml \
                ./cspsubarrayleafnode/build/reports/cspsubarrayleafnode-unit-tests.xml \
                ./dishleafnode/build/reports/dishleafnode-unit-tests.xml \
                ./sdpmasterleafnode/build/reports/sdpmasterleafnode-unit-tests.xml \
                ./sdpsubarrayleafnode/build/reports/sdpsubarrayleafnode-unit-tests.xml \
                ./subarraynode/build/reports/subarraynode-unit-tests.xml \
                ../build/reports/tox_unit-tests.xml
