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
# 	retry --max=10 -- tango_admin --ping-device mid_d0001/elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_d0002/elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_d0003/elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_d0004/elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_csp_cbf/sub_elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_csp/elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_csp/elt/subarray_01
# 	retry --max=10 -- tango_admin --ping-device mid_csp_cbf/sub_elt/subarray_01
# 	retry --max=10 -- tango_admin --ping-device mid_sdp/elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_csp/elt/master
# 	retry --max=10 -- tango_admin --ping-device mid_sdp/elt/subarray_1
# 	retry --max=10 -- tango_admin --ping-device mid_csp/elt/subarray_01
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0001
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0002
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0003
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0004
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/sdp_master
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/csp_master
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/sdp_subarray01
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/csp_subarray01
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/1
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/2
# 	retry --max=10 -- tango_admin --ping-device ska_mid/tm_central/central_node

	cd /app/tmcprototype/DishMaster && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/DishMaster/dishmaster_coverage /build/dishmaster_coverage
	cd /app/tmcprototype/DishLeafNode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/DishLeafNode/dishleafnode_coverage /build/dishleafnode_coverage
	cd /app/tmcprototype/CspMasterLeafNode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/CspMasterLeafNode/cspmasterleafnode_coverage /build/cspmasterleafnode_coverage
	cd /app/tmcprototype/CspSubarrayLeafNode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/CspSubarrayLeafNode/cspsubarrayleafnode_coverage /build/cspsubarrayleafnode_coverage
	cd /app/tmcprototype/SdpMasterLeafNode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/SdpMasterLeafNode/sdpmasterleafnode_coverage /build/sdpmasterleafnode_coverage
	cd /app/tmcprototype/SdpSubarrayLeafNode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/SdpSubarrayLeafNode/sdpsubarrayleafnode_coverage /build/sdpsubarrayleafnode_coverage
	cd /app/tmcprototype/SubarrayNode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/SubarrayNode/subarraynode_coverage /build/subarraynode_coverage
	cd /app/tmcprototype/CentralNode && python setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/CentralNode/centralnode_coverage /build/centralnode_coverage
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

	mv /app/tmcprototype/DishMaster/setup_py_test.stdout /build/dishmaster_setup_py_test.stdout; \
	mv /app/tmcprototype/DishMaster/htmlcov /build/dishmaster_htmlcov; \
	mv /app/tmcprototype/CspSubarrayLeafNode/setup_py_test.stdout /build/cspsubarrayleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/CspSubarrayLeafNode/htmlcov /build/cspsubarrayleafnode_htmlcov; \
	mv /app/tmcprototype/DishLeafNode/setup_py_test.stdout /build/dishleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/DishLeafNode/htmlcov /build/dishleafnode_htmlcov; \
	mv /app/tmcprototype/SdpSubarrayLeafNode/setup_py_test.stdout /build/sdpsubarrayleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/SdpSubarrayLeafNode/htmlcov /build/sdpsubarrayleafnode_htmlcov; \
	mv /app/tmcprototype/CspMasterLeafNode/setup_py_test.stdout /build/cspmasterleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/CspMasterLeafNode/htmlcov /build/cspmasterleafnode_htmlcov; \
	mv /app/tmcprototype/SdpMasterLeafNode/setup_py_test.stdout /build/sdpmasterleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/SdpMasterLeafNode/htmlcov /build/sdpmasterleafnode_htmlcov; \
	mv /app/tmcprototype/SubarrayNode/setup_py_test.stdout /build/subarraynode_setup_py_test.stdout; \
	mv /app/tmcprototype/SubarrayNode/htmlcov /build/subarraynode_htmlcov; \
	mv /app/tmcprototype/CentralNode/setup_py_test.stdout /build/centralnode_setup_py_test.stdout; \
	mv /app/tmcprototype/CentralNode/htmlcov /build/centralnode_htmlcov; \

lint:
	pip3 install pylint2junit junitparser; \
	mkdir -p /build/reports; \
# Code analysis of all the devices/packages using pylint
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/DishMaster | tee /build/dish-master-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/CspSubarrayLeafNode | tee /build/csp-subarray-leaf-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/DishLeafNode | tee /build/dish-leaf-node-code_analysis.stdout;
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/SdpSubarrayLeafNode | tee /build/sdp-subarray-leaf-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/CspMasterLeafNode | tee /build/csp-master-leaf-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/SdpMasterLeafNode | tee /build/sdp-master-leaf-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/SubarrayNode | tee /build/subarray-node-code_analysis.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR)/CentralNode | tee /build/central-node-code_analysis.stdout; \
# Generate device-linting.xml files for all the devices/packages
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/DishMaster > /build/dish-master-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/CspSubarrayLeafNode > /build/csp-subarray-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/DishLeafNode > /build/dish-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/SdpSubarrayLeafNode > /build/sdp-subarray-leaf-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/CspMasterLeafNode > /build/csp-master-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/SdpMasterLeafNode > /build/sdp-master-leaf-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/SubarrayNode > /build/subarray-node-linting.xml; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR)/CentralNode > /build/central-node-linting.xml; \
# Merge device-linting.xml files of all the packages/devices into single linting.xml file
	junitparser merge /build/dish-master-linting.xml /build/csp-subarray-leaf-node-linting.xml \
	 /build/dish-leaf-node-linting.xml /build/sdp-subarray-leaf-linting.xml \
	 /build/csp-master-leaf-node-linting.xml /build/sdp-master-leaf-node-linting.xml \
	 /build/subarray-node-linting.xml /build/central-node-linting.xml /build/reports/linting.xml

.PHONY: all test lint
