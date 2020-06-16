#!/bin/bash
#Entering into a bash shell script to run unit-test cases and generating reports
cd /app/tmcprototype;

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo $TMC_ELEMENT;
	echo +++ Trying tests for $TMC_ELEMENT;
	pytest -v ./${TMC_ELEMENT}/test/unit --forked --cov=/venv/lib/python3.7/site-packages/${TMC_ELEMENT} --cov-report=html:/report/unitTest/${TMC_ELEMENT}_htmlcov --json-report --json-report-file=/report/unitTest/${TMC_ELEMENT}_report.json --junitxml=/report/unitTest/${TMC_ELEMENT}-unit-tests.xml;
  mv /app/tmcprototype/.coverage /report/unitTest/${TMC_ELEMENT}_coverage;
done
cd /report/unitTest
coverage combine dishleafnode_coverage cspmasterleafnode_coverage \
	 cspsubarrayleafnode_coverage sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
	 subarraynode_coverage centralnode_coverage  && coverage xml && coverage html
mv /report/unitTest/coverage.xml /report/code-coverage.xml
pip3 install junitparser
junitparser merge /report/unitTest/dishleafnode-unit-tests.xml \
                /report/unitTest/centralnode-unit-tests.xml \
                /report/unitTest/cspmasterleafnode-unit-tests.xml \
                /report/unitTest/cspsubarrayleafnode-unit-tests.xml \
                /report/unitTest/sdpmasterleafnode-unit-tests.xml \
                /report/unitTest/sdpsubarrayleafnode-unit-tests.xml \
                /report/unitTest/subarraynode-unit-tests.xml \
                /report/unitTest/unit-tests.xml
mv /report/unitTest/unit-tests.xml /report/unit-tests.xml




