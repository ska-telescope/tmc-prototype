#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "Coding analysis will be performed shortly..."
python3 -m pip install pylint2junit junitparser; \
python3 -m pip install --index-url https://artefact.skao.int/repository/pypi-internal/simple  ska-ser-logging==0.4.0 ska-tmc-cdm==6.0.0 ska-tmc-common==0.1.7+d39e6423 ska-telescope-model==1.3.1 ska-ser-log-transactions ska-tango-base == 0.7.2
for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo +++ Trying tests for $TMC_ELEMENT;
	cd $TMC_ELEMENT;
	python3 -m pip install .;
  cd ..
done

cd ../
mkdir -p ./build/reports; \
pylint --rcfile=.pylintrc --output-format=parseable ska-tmc | tee ./build/reports/linting.stdout; \
pylint --rcfile=.pylintrc --output-format=pylint2junit.JunitReporter ska-tmc > ./build/reports/linting.xml;
