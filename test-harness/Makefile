# Use bash shell with pipefail option enabled so that the return status of a
# piped command is the value of the last (rightmost) commnand to exit with a
# non-zero status. This lets us pipe output into tee but still exit on test
# failures.
SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -c

all: test

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
test:
	retry --max=10 -- tango_admin --ping-device mid_d0001/elt/master
	retry --max=10 -- tango_admin --ping-device mid_d0002/elt/master
	retry --max=10 -- tango_admin --ping-device mid_d0003/elt/master
	retry --max=10 -- tango_admin --ping-device mid_d0004/elt/master
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/csp_subarray
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0001
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0002
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0003
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/d0004
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_leaf_node/sdp_subarray
	retry --max=10 -- tango_admin --ping-device mid_csp_cbf/sub_elt/master
	retry --max=10 -- tango_admin --ping-device mid_csp/elt/master
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/1
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_subarray_node/2
	retry --max=10 -- tango_admin --ping-device mid_sdp/elt/subarray_1
	retry --max=10 -- tango_admin --ping-device mid-csp/elt/subarray01
	retry --max=10 -- tango_admin --ping-device ska_mid/tm_central/central_node

	cd /app/tmcprototype/DishMaster && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/CspSubarrayLeafNode && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/DishLeafNode && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/SdpSubarrayLeafNode && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/CspMasterLeafNode && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/CspSubarray && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/SubarrayNode && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/CentralNode && python setup.py test | tee setup_py_test.stdout
	cd /app && ./code-analysis.sh | tee code_analysis.stdout
	if [ -d /build ]; then \
        mv /app/tmcprototype/DishMaster/setup_py_test.stdout /build/dishmaster_setup_py_test.stdout; \
        mv /app/tmcprototype/DishMaster/htmlcov /build/dishmaster_htmlcov; \
        mv /app/tmcprototype/DishMaster/coverage.xml /build/dishmaster_coverage.xml; \
        mv /app/tmcprototype/CspSubarrayLeafNode/setup_py_test.stdout /build/cspsubarrayleafnode_setup_py_test.stdout; \
        mv /app/tmcprototype/CspSubarrayLeafNode/htmlcov /build/cspsubarrayleafnode_htmlcov; \
        mv /app/tmcprototype/CspSubarrayLeafNode/coverage.xml /build/cspsubarrayleafnode_coverage.xml; \
        mv /app/tmcprototype/DishLeafNode/setup_py_test.stdout /build/dishleafnode_setup_py_test.stdout; \
        mv /app/tmcprototype/DishLeafNode/htmlcov /build/dishleafnode_htmlcov; \
        mv /app/tmcprototype/DishLeafNode/coverage.xml /build/dishleafnode_coverage.xml; \
        mv /app/tmcprototype/SdpSubarrayLeafNode/coverage.xml /build/sdpsubarrayleafnode_coverage.xml; \
        mv /app/tmcprototype/CspMasterLeafNode/setup_py_test.stdout /build/cspmasterleafnode_setup_py_test.stdout; \
        mv /app/tmcprototype/CspMasterLeafNode/htmlcov /build/cspmasterleafnode_htmlcov; \
        mv /app/tmcprototype/CspMasterLeafNode/coverage.xml /build/cspmasterleafnode_coverage.xml; \
        mv /app/tmcprototype/SubarrayNode/setup_py_test.stdout /build/subarraynode_setup_py_test.stdout; \
        mv /app/tmcprototype/SubarrayNode/htmlcov /build/subarraynode_htmlcov; \
        mv /app/tmcprototype/SubarrayNode/coverage.xml /build/subarraynode_coverage.xml; \
        mv /app/tmcprototype/CentralNode/setup_py_test.stdout /build/centralnode_setup_py_test.stdout; \
        mv /app/tmcprototype/CentralNode/htmlcov /build/centralnode_htmlcov; \
        mv /app/tmcprototype/CentralNode/coverage.xml /build/centralnode_coverage.xml; \
        mv /app/tmcprototype/CspSubarray/setup_py_test.stdout /build/cspsubarray_setup_py_test.stdout; \
        mv /app/tmcprototype/CspSubarray/htmlcov /build/cspsubarray_htmlcov; \
        mv /app/tmcprototype/CspSubarray/coverage.xml /build/cspsubarray_coverage.xml; \
        mv /app/code_analysis.stdout /build/tmcprototype_code_analysis.stdout; \
    fi;
.PHONY: all test
