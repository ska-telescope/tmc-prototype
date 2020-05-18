#!/bin/bash
cd /app/tmcprototype;
#mkdir test_results;
for path in $(find ./*/test  -type d -name unit); do
echo $path;
export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
echo $TMC_ELEMENT;
echo +++ Trying tests for $TMC_ELEMENT;
pytest -v ./${TMC_ELEMENT}/test/unit --forked --cov=./${TMC_ELEMENT} --cov-report=html:/report/${TMC_ELEMENT}_htmlcov --json-report --json-report-file=/report/${TMC_ELEMENT}_report.json --junitxml=/report/${TMC_ELEMENT}-unit-tests.xml;
ls -l /report;
#mv test_results/${TMC_ELEMENT}_htmlcov /snehal;
#ls -l /snehal;
done
echo after for loop;
ls -l /report;
mv /report /local_report;
echo In local report;
ls -l local_report

#mv /app/tmcprototype/test_results/* /build/unit_test_result
#mv /app/tmcprototype/dishmaster/test_results/* /build/unit_test_result/dishmaster \
#mv /app/tmcprototype/cspsubarrayleafnode/test_results/* /build/unit_test_result/cspsubarrayleafnode \
#mv /app/tmcprototype/dishleafnode/test_results/* /build/unit_test_result/dishleafnode \
#mv /app/tmcprototype/sdpsubarrayleafnode/test_results/* /build/unit_test_result/sdpsubarrayleafnode \
#mv /app/tmcprototype/cspmasterleafnode/test_results/* /build/unit_test_result/cspmasterleafnode \
#mv /app/tmcprototype/cspsubarrayleafnode/test_results/* /build/unit_test_result/cspsubarrayleafnode \
#mv /app/tmcprototype/sdpmasterleafnode/test_results/* /build/unit_test_result/sdpmasterleafnode \
#mv /app/tmcprototype/subarraynode/test_results/* /build/unit_test_result/subarraynode \
#mv /app/tmcprototype/centralnode/test_results/* /build/unit_test_result/centralnode
