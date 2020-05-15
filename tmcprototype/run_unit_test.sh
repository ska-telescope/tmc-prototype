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

mv /app/tmcprototype/dishmaster/test_results/* /build/unit_test_result/dishmaster \
mv /app/tmcprototype/cspsubarrayleafnode/test_results/* /build/unit_test_result/cspsubarrayleafnode \
mv /app/tmcprototype/dishleafnode/test_results/* /build/unit_test_result/dishleafnode \
mv /app/tmcprototype/sdpsubarrayleafnode/test_results/* /build/unit_test_result/sdpsubarrayleafnode \
mv /app/tmcprototype/cspmasterleafnode/test_results/* /build/unit_test_result/cspmasterleafnode \
mv /app/tmcprototype/cspsubarrayleafnode/test_results/* /build/unit_test_result/cspsubarrayleafnode \
mv /app/tmcprototype/sdpmasterleafnode/test_results/* /build/unit_test_result/sdpmasterleafnode \
mv /app/tmcprototype/subarraynode/test_results/* /build/unit_test_result/subarraynode \
mv /app/tmcprototype/centralnode/test_results/* /build/unit_test_result/centralnode
