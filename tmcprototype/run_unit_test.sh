#!/bin/bash
#Entering into a bash shell script to run unit-test cases and generating reports
cd /app/tmcprototype;

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo $TMC_ELEMENT;
	echo +++ Trying tests for $TMC_ELEMENT;
	pytest -v ./${TMC_ELEMENT}/test/unit --forked --cov=/venv/lib/python3.7/site-packages/${TMC_ELEMENT} --cov-report=html:/report/${TMC_ELEMENT}_htmlcov --json-report --json-report-file=/report/${TMC_ELEMENT}_report.json --junitxml=/report/${TMC_ELEMENT}-unit-tests.xml;
  mv /app/tmcprototype/.coverage /report/${TMC_ELEMENT}_coverage;
done
cd /report
coverage combine dishleafnode_coverage cspmasterleafnode_coverage \
	 cspsubarrayleafnode_coverage sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
	 subarraynode_coverage centralnode_coverage  && coverage xml && coverage html
pip3 install junitparser
junitparser merge /report/dishleafnode-unit-tests.xml \
                /report/centralnode-unit-tests.xml \
                /report/cspmasterleafnode-unit-tests.xml \
                /report/cspsubarrayleafnode-unit-tests.xml \
                /report/sdpmasterleafnode-unit-tests.xml \
                /report/sdpsubarrayleafnode-unit-tests.xml \
                /report/subarraynode-unit-tests.xml \
                /report/unit-tests.xml

