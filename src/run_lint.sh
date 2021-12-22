#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "Coding analysis will be performed shortly..."
python3 -m pip install pylint2junit junitparser; \
python3 -m pip install --index-url https://artefact.skao.int/repository/pypi-internal/simple -r ../requirements.txt; \
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
