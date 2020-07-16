#!/bin/bash
#Entering into a bash shell script to run unit-test cases and generating reports
cd /app/tmcprototype;
python3 -m pip install pytest-forked

#For each node sub-package inside tmc-prototype, coverage report for each device is generated using unit-test job.
#Coverage report are generated in .coverage, .xml and .html format. Each device's .coverage report is moved in unit_test folder to generate the combine report further.
for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo $TMC_ELEMENT;
	echo +++ Trying tests for $TMC_ELEMENT;
	pytest -v ./${TMC_ELEMENT}/test/unit --forked --cov=/usr/local/lib/python3.7/dist-packages/${TMC_ELEMENT} --cov-report=html:/report/unit_test/${TMC_ELEMENT}_htmlcov --json-report --json-report-file=/report/unit_test/${TMC_ELEMENT}_report.json --junitxml=/report/unit_test/${TMC_ELEMENT}-unit-tests.xml;
	mv /app/tmcprototype/.coverage /report/unit_test/${TMC_ELEMENT}_coverage;
done
cd /report/unit_test
#Combine the individual report in combine converage report in xml and html format.
coverage combine dishleafnode_coverage cspmasterleafnode_coverage \
	 cspsubarrayleafnode_coverage sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
	 subarraynode_coverage centralnode_coverage  && coverage xml && coverage html
mv /report/unit_test/coverage.xml /report/code-coverage.xml
#Combine the unit_test.xml reports
python3 -m pip install junitparser
junitparser merge /report/unit_test/dishleafnode-unit-tests.xml \
                /report/unit_test/centralnode-unit-tests.xml \
                /report/unit_test/cspmasterleafnode-unit-tests.xml \
                /report/unit_test/cspsubarrayleafnode-unit-tests.xml \
                /report/unit_test/sdpmasterleafnode-unit-tests.xml \
                /report/unit_test/sdpsubarrayleafnode-unit-tests.xml \
                /report/unit_test/subarraynode-unit-tests.xml \
                /report/unit_test/unit-tests.xml
mv /report/unit_test/unit-tests.xml /report/unit-tests.xml
