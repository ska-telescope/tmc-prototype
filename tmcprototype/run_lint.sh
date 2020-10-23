#!/bin/bash
set -eo pipefail
#Entering into a bash shell script to run unit-test cases and generating reports
echo "Coding analysis will be performed shortly..."
python3 -m pip install pylint2junit junitparser; \
python3 -m pip install --index-url https://nexus.engageska-portugal.pt/repository/pypi/simple ska-logging==0.3.0 lmcbaseclasses==0.7.1 cdm-shared-library==2.0.0 ska-telescope-model==0.1.4 

for path in $(find ./*/test  -type d -name unit); do
	export TMC_ELEMENT=$(basename $(dirname $(dirname $path)));
	echo +++ Trying tests for $TMC_ELEMENT;
	cd $TMC_ELEMENT;
	python3 -m pip install .;
  cd ..
done

cd ../
mkdir -p ./build/reports; \
pylint --rcfile=.pylintrc --output-format=parseable tmcprototype | tee ./build/reports/linting.stdout; \
pylint --rcfile=.pylintrc --output-format=pylint2junit.JunitReporter tmcprototype > ./build/reports/linting.xml;
