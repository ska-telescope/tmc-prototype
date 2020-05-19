#!/bin/bash
#Entering into a bash shell script to run unit-test cases and generating reports
cd /app/tmcprototype;

for path in $(find ./*/test  -type d -name unit); do
	echo $path;
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo $TMC_ELEMENT;
	echo +++ Trying tests for $TMC_ELEMENT;
	pytest -v ./${TMC_ELEMENT}/test/unit --forked --cov=/venv/lib/python3.7/site-packages/${TMC_ELEMENT} --cov-report=html:/report/${TMC_ELEMENT}_htmlcov --json-report --json-report-file=/report/${TMC_ELEMENT}_report.json --junitxml=/report/${TMC_ELEMENT}-unit-tests.xml;
done

