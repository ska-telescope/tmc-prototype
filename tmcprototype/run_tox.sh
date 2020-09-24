#!/bin/bash
set -eo pipefail
echo "Check current directory"
pwd
ls
export working_dir=../build/reports/tox_report
echo "moving back to a check build dir "
#ls ../build/reports/  <- gives error sometimes: No such file or directory
#Entering into a bash shell script to run unit-test cases and generating reports
echo "In run_tox file...."
mkdir -p tox_report
if [ -d "$working_dir" ]; then rm -rf $working_dir; fi

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo +++ Trying tests for $TMC_ELEMENT;
	cd $TMC_ELEMENT
	tox -e py37
  mv ${TMC_ELEMENT}_coverage ../tox_report/${TMC_ELEMENT}_coverage
done

#cd centralnode
#tox -e py37
#mv centralnode_coverage ../tox_report/centralnode_coverage
#cd ../cspmasterleafnode
#tox -e py37
#mv cspmasterleafnode_coverage ../tox_report/cspmasterleafnode_coverage
#cd ../cspsubarrayleafnode
#tox -e py37
#mv cspsubarrayleafnode_coverage ../tox_report/cspsubarrayleafnode_coverage
#cd ../dishleafnode
#tox -e py37
#mv dishleafnode_coverage ../tox_report/dishleafnode_coverage
#cd ../sdpmasterleafnode
#tox -e py37
#mv sdpmasterleafnode_coverage ../tox_report/sdpmasterleafnode_coverage
#cd ../sdpsubarrayleafnode
#tox -e py37
#mv sdpsubarrayleafnode_coverage ../tox_report/sdpsubarrayleafnode_coverage
#cd ../subarraynode
#tox -e py37
#mv subarraynode_coverage ../tox_report/subarraynode_coverage

echo "Came out of Loop..."
pwd
ls
echo "-----------------------------------------------------"
cd ../
echo "check for tox_report"
ls
echo "Checking content from tox_report"
ls tox_report
echo "check build/reports before moving tox_report"
ls ../build/reports
mv ./tox_report ../build/reports
echo "check if tox_report is moved"
ls ../build/reports
cd ../build/reports/tox_report
echo "Checking tox_report is present or not?"
ls

# # # Combine coverage reports
coverage combine centralnode_coverage cspmasterleafnode_coverage \
                  cspsubarrayleafnode_coverage dishleafnode_coverage \
                  sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
                  subarraynode_coverage && coverage xml
pwd
cd ..
cd ./tox_report && mv coverage.xml ../tox_code-coverage.xml
cd ../../../tmcprototype
echo "In tmcprototype"
pwd
ls
echo "check content present in each tmc package build folder"
ls ./centralnode/build/htmlcov
python3 -m pip install junitparser
junitparser merge ./centralnode/build/reports/centralnode-unit-tests.xml \
                ./cspmasterleafnode/build/reports/cspmasterleafnode-unit-tests.xml \
                ./cspsubarrayleafnode/build/reports/cspsubarrayleafnode-unit-tests.xml \
                ./dishleafnode/build/reports/dishleafnode-unit-tests.xml \
                ./sdpmasterleafnode/build/reports/sdpmasterleafnode-unit-tests.xml \
                ./sdpsubarrayleafnode/build/reports/sdpsubarrayleafnode-unit-tests.xml \
                ./subarraynode/build/reports/subarraynode-unit-tests.xml \
                ../build/reports/tox_unit-tests.xml
ls