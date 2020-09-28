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
	retry --max=10 -- tango_admin --ping-device ska_low/tm_leaf_node/mccs_master
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/sdp_subarray01
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/csp_subarray01
	retry --max=10 -- tango_admin --ping-device ska_low/tm_leaf_node/mccs_subarray01
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/1
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/2
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_central/central_node

	cd /app/tmcprototype/dishmaster && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/dishmaster/dishmaster_coverage /build/dishmaster_coverage
	cd /app/tmcprototype/dishleafnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/dishleafnode/dishleafnode_coverage /build/dishleafnode_coverage
	cd /app/tmcprototype/cspmasterleafnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/cspmasterleafnode/cspmasterleafnode_coverage /build/cspmasterleafnode_coverage
	cd /app/tmcprototype/cspsubarrayleafnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/cspsubarrayleafnode/cspsubarrayleafnode_coverage /build/cspsubarrayleafnode_coverage
	cd /app/tmcprototype/sdpmasterleafnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/sdpmasterleafnode/sdpmasterleafnode_coverage /build/sdpmasterleafnode_coverage
	cd /app/tmcprototype/mccsmasterleafnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/mccsmasterleafnode/mccsmasterleafnode_coverage /build/mccsmasterleafnode_coverage
	cd /app/tmcprototype/sdpsubarrayleafnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/sdpsubarrayleafnode/sdpsubarrayleafnode_coverage /build/sdpsubarrayleafnode_coverage
	cd /app/tmcprototype/mccssubarrayleafnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/mccssubarrayleafnode/mccssubarrayleafnode_coverage /build/mccssubarrayleafnode_coverage
	cd /app/tmcprototype/subarraynode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/subarraynode/subarraynode_coverage /build/subarraynode_coverage
	cd /app/tmcprototype/centralnode && python3 setup.py test --addopts='-k-unit' | tee setup_py_test.stdout
	mv /app/tmcprototype/centralnode/centralnode_coverage /build/centralnode_coverage
	# Combine raw output from the coverage files of all the packages/devices and export to XML file
	cd /build && coverage combine dishmaster_coverage dishleafnode_coverage cspmasterleafnode_coverage \
	 cspsubarrayleafnode_coverage sdpmasterleafnode_coverage sdpsubarrayleafnode_coverage mccsmasterleafnode_coverage \
	 mccssubarrayleafnode_coverage subarraynode_coverage centralnode_coverage  && coverage xml && coverage html
	mkdir -p /build/reports
#renamed code-coverage to runtest-code-coverage as unit test cases combined coverage report is saved as code-coverage.xml in order to create badge with coverage report from mocking test case result.
	cd /build && mv coverage.xml ./reports/runtest-code-coverage.xml

	# Merge device-unit-tests.xml files of all the packages/devices into single unit-tests.xml file. Renamed unit-tests.xml to runtest-code-coverage as unit test cases combined coverage report is saved as runtest-unit-tests.xml in order to create badge with coverage report from mocking test case result.
	python3 -m pip install junitparser
	junitparser merge /build/reports/dish-leaf-node-unit-tests.xml \
                             /build/reports/dish-master-unit-tests.xml \
                             /build/reports/central-node-unit-tests.xml \
                             /build/reports/csp-master-leaf-node-unit-tests.xml \
                             /build/reports/csp-subarray-leaf-node-unit-tests.xml \
                             /build/reports/sdp-master-leaf-node-unit-tests.xml \
                             /build/reports/sdp-subarray-leaf-node-unit-tests.xml \
                             /build/reports/mccs-master-leaf-node-unit-tests.xml \
                             /build/reports/mccs-subarray-leaf-node-unit-tests.xml \
                             /build/reports/subarraynode-unit-tests.xml \
                             /build/reports/runtest-unit-tests.xml
	cd /build/reports && rm dish-leaf-node-unit-tests.xml dish-master-unit-tests.xml mccs-master-leaf-node-unit-tests.xml \
	 central-node-unit-tests.xml csp-master-leaf-node-unit-tests.xml csp-subarray-leaf-node-unit-tests.xml mccs-subarray-leaf-node-unit-tests.xml \
	 sdp-master-leaf-node-unit-tests.xml sdp-subarray-leaf-node-unit-tests.xml subarraynode-unit-tests.xml \

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
	mv /app/tmcprototype/mccsmasterleafnode/setup_py_test.stdout /build/mccsmasterleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/mccsmasterleafnode/htmlcov /build/mccsmasterleafnode_htmlcov; \
	mv /app/tmcprototype/mccssubarrayleafnode/setup_py_test.stdout /build/mccssubarrayleafnode_setup_py_test.stdout; \
	mv /app/tmcprototype/mccssubarrayleafnode/htmlcov /build/mccssubarrayleafnode_htmlcov; \
	mv /app/tmcprototype/subarraynode/setup_py_test.stdout /build/subarraynode_setup_py_test.stdout; \
	mv /app/tmcprototype/subarraynode/htmlcov /build/subarraynode_htmlcov; \
	mv /app/tmcprototype/centralnode/setup_py_test.stdout /build/centralnode_setup_py_test.stdout; \
	mv /app/tmcprototype/centralnode/htmlcov /build/centralnode_htmlcov; \

lint:
	python3 -m pip install pylint2junit junitparser; \
	mkdir -p /build/reports; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=parseable $(TMC_ROOT_DIR) | tee /build/reports/linting.stdout; \
	pylint --rcfile=$(SRC_ROOT_DIR)/.pylintrc --output-format=pylint2junit.JunitReporter $(TMC_ROOT_DIR) > /build/reports/linting.xml;

.PHONY: all test lint
