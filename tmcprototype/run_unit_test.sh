#!/bin/bash
cd /app/tmcprototype;
mkdir test_results;
for path in $(find ./*/test  -type d -name unit); do
echo $path;  
export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
echo $TMC_ELEMENT;
echo +++ Trying tests for $TMC_ELEMENT;
pytest -v ./${TMC_ELEMENT}/test/unit --forked --cov=./${TMC_ELEMENT} --cov-report=html:./test_results/${TMC_ELEMENT}_htmlcov --json-report --json-report-file=./test_results/${TMC_ELEMENT}_report.json --junitxml=./test_results/${TMC_ELEMENT}-unit-tests.xml;
done 

