# Use bash shell with pipefail option enabled so that the return status of a
# piped command is the value of the last (rightmost) command to exit with a
# non-zero status. This lets us pipe output into tee but still exit on test
# failures.
SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -c

SRC_ROOT_DIR := /app
TMC_ROOT_DIR := $(SRC_ROOT_DIR)/tmcprototype

all: test lint

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
test:
	retry --max=10 -- tango_admin --ping-device mid_d0001/elt/master
	retry --max=10 -- tango_admin --ping-device mid_d0002/elt/master
	retry --max=10 -- tango_admin --ping-device mid_d0003/elt/master
	retry --max=10 -- tango_admin --ping-device mid_d0004/elt/master
	retry --max=10 -- tango_admin --ping-device mid_csp_cbf/sub_elt/master
	retry --max=10 -- tango_admin --ping-device mid_csp/elt/master
	retry --max=10 -- tango_admin --ping-device mid_csp/elt/subarray_01
	retry --max=10 -- tango_admin --ping-device mid_csp_cbf/sub_elt/subarray_01
	retry --max=10 -- tango_admin --ping-device mid_sdp/elt/master
	retry --max=10 -- tango_admin --ping-device mid_csp/elt/master
	retry --max=10 -- tango_admin --ping-device mid_sdp/elt/subarray_1
	retry --max=10 -- tango_admin --ping-device mid_csp/elt/subarray_01
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0001
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0002
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0003
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0004
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/sdp_master
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/csp_master
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/sdp_subarray01
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/csp_subarray01
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/1
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/2
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_central/central_node

# 	cd /app/tmcprototype/dishmaster && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
# 	mv /app/tmcprototype/dishmaster/dishmaster_coverage /build/dishmaster_coverage
# 	cd /app/tmcprototype/dishleafnode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
# 	mv /app/tmcprototype/dishleafnode/dishleafnode_coverage /build/dishleafnode_coverage
    cd /app/tmcprototype/cspmasterleafnode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
    mv /app/tmcprototype/cspmasterleafnode/cspmasterleafnode_coverage /build/cspmasterleafnode_coverage
    cd /app/tmcprototype/cspsubarrayleafnode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
    mv /app/tmcprototype/cspsubarrayleafnode/cspsubarrayleafnode_coverage /build/cspsubarrayleafnode_coverage
# 	cd /app/tmcprototype/sdpmasterleafnode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
# 	mv /app/tmcprototype/sdpmasterleafnode/sdpmasterleafnode_coverage /build/sdpmasterleafnode_coverage
# 	cd /app/tmcprototype/sdpsubarrayleafnode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
# 	mv /app/tmcprototype/sdpsubarrayleafnode/sdpsubarrayleafnode_coverage /build/sdpsubarrayleafnode_coverage
# 	cd /app/tmcprototype/subarraynode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
# 	mv /app/tmcprototype/subarraynode/subarraynode_coverage /build/subarraynode_coverage
# 	cd /app/tmcprototype/centralnode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
# 	mv /app/tmcprototype/centralnode/centralnode_coverage /build/centralnode_coverage
	# Combine raw output from the coverage files of all the packages/devices and export to XML file
	cd /build && coverage combine dishmaster_coverage dishleafnode_coverage cspmasterleafnode_coverage \
	 cspsubarrayleafnode_coverage sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage \
	 subarraynode_coverage centralnode_coverage  && coverage xml && coverage html
	mkdir -p /build/reports
	cd /build && mv coverage.xml ./reports/code-coverage.xml

	# Merge device-unit-tests.xml files of all the packages/devices into single unit-tests.xml file
	pip3 install junitparser
	junitparser merge /build/reports/dish-leaf-node-unit-tests.xml \
                             /build/reports/dish-master-unit-tests.xml \
                             /build/reports/central-node-unit-tests.xml \
                             /build/reports/csp-master-leaf-node-unit-tests.xml \
                             /build/reports/csp-subarray-leaf-node-unit-tests.xml \
                             /build/reports/sdp-master-leaf-node-unit-tests.xml \
                             /build/reports/sdp-subarray-leaf-node-unit-tests.xml \
                             /build/reports/subarraynode-unit-tests.xml \
                             /build/reports/unit-tests.xml
	cd /build/reports && rm dish-leaf-node-unit-tests.xml dish-master-unit-tests.xml \
	 central-node-unit-tests.xml csp-master-leaf-node-unit-tests.xml csp-subarray-leaf-node-unit-tests.xml \
	 sdp-master-leaf-node-unit-tests.xml sdp-subarray-leaf-node-unit-tests.xml subarraynode-unit-tests.xml

	mv /app/tmcprototype/dishmaster/setup_py_test.stdout /build/dishmaster_setup_py_test.stdout; \
	mv /app/tmcprototype/dishmaster/htmlcov /build/dishmaster_htmlcov; \
	mv /app/tmcprototype/cspsubarrayleafnode/setup_py_test.stdout /build/cspsubarrayleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/cspsubarrayleafnode/htmlcov /build/cspsubarrayleafnode_htmlcov; \
	mv /app/tmcprototype/dishleafnode/setup_py_test.stdout /build/dishleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/dishleafnode/htmlcov /build/dishleafnode_htmlcov; \
	mv /app/tmcprototype/sdpsubarrayleafnode/setup_py_test.stdout /build/sdpsubarrayleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/sdpsubarrayleafnode/htmlcov /build/sdpsubarrayleafnode_htmlcov; \
	mv /app/tmcprototype/cspmasterleafnode/setup_py_test.stdout /build/cspmasterleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/cspmasterleafnode/htmlcov /build/cspmasterleafnode_htmlcov; \
	mv /app/tmcprototype/sdpmasterleafnode/setup_py_test.stdout /build/sdpmasterleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/sdpmasterleafnode/htmlcov /build/sdpmasterleafnode_htmlcov; \
	mv /app/tmcprototype/subarraynode/setup_py_test.stdout /build/subarraynode_setup_py_test.stdout; \
	mv /app/tmcprototype/subarraynode/htmlcov /build/subarraynode_htmlcov; \
	mv /app/tmcprototype/centralnode/setup_py_test.stdout /build/centralnode_setup_py_test.stdout; \
	mv /app/tmcprototype/centralnode/htmlcov /build/centralnode_htmlcov; \

lint:
	pip3 install pylint2junit junitparser; \
	mkdir -p /build/reports;
# Code analysis of all the devices/packages using pylint
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/dishmaster/src/dishmaster | tee /build/dish-master-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/cspsubarrayleafnode/src/cspsubarrayleafnode | tee /build/csp-subarray-leaf-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/dishleafnode/src/dishleafnode | tee /build/dish-leaf-node-code_analysis.stdout;
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/sdpsubarrayleafnode/src/sdpsubarrayleafnode | tee /build/sdp-subarray-leaf-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/cspmasterleafnode/src/cspmasterleafnode | tee /build/csp-master-leaf-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/sdpmasterleafnode/src/sdpmasterleafnode | tee /build/sdp-master-leaf-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/subarraynode/src/subarraynode | tee /build/subarray-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/centralnode/src/centralnode | tee /build/central-node-code_analysis.stdout;
# Generate device-linting.xml files for all the devices/packages
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/dishmaster/src/dishmaster > /build/dish-master-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/cspsubarrayleafnode/src/cspsubarrayleafnode > /build/csp-subarray-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/dishleafnode/src/dishleafnode > /build/dish-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/sdpsubarrayleafnode/src/sdpsubarrayleafnode > /build/sdp-subarray-leaf-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/cspmasterleafnode/src/cspmasterleafnode > /build/csp-master-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/sdpmasterleafnode/src/sdpmasterleafnode > /build/sdp-master-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/subarraynode/src/subarraynode > /build/subarray-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/centralnode/src/centralnode > /build/central-node-linting.xml;
# Merge device-linting.xml files of all the packages/devices into single linting.xml file
	junitparser merge /build/dish-master-linting.xml /build/csp-subarray-leaf-node-linting.xml \
	 /build/dish-leaf-node-linting.xml /build/sdp-subarray-leaf-linting.xml \
	 /build/csp-master-leaf-node-linting.xml /build/sdp-master-leaf-node-linting.xml \
	 /build/subarray-node-linting.xml /build/central-node-linting.xml /build/reports/linting.xml

.PHONY: all test lint
