all: test

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
test:
	retry -- tango_admin --check-device test/DishMaster/01
	ls -ls
	cd /app/tmcprototype/DishMaster && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/DishMaster && ./code-analysis.sh | tee code_analysis.stdout
	cd /app/tmcprototype/DishLeafNode && python setup.py test | tee setup_py_test.stdout
	cd /app/tmcprototype/DishLeafNode && ./code-analysis.sh | tee code_analysis.stdout
	if [ -d /build ]; then \
        mv /app/tmcprototype/DishMaster/setup_py_test.stdout /build/dishmaster_setup_py_test.stdout; \
        mv /app/tmcprototype/DishMaster/code_analysis.stdout /build/dishmaster_code_analysis.stdout; \
        mv /app/tmcprototype/DishMaster/htmlcov /build/dishmaster_htmlcov; \
        mv /app/tmcprototype/DishMaster/coverage.xml /build/dishmaster_coverage.xml; \
        mv /app/tmcprototype/DishLeafNode/setup_py_test.stdout /build/dishleafnode_setup_py_test.stdout; \
        mv /app/tmcprototype/DishLeafNode/code_analysis.stdout /build/dishleafnode_code_analysis.stdout; \
        mv /app/tmcprototype/DishLeafNode/htmlcov /build/dishleafnode_htmlcov; \
        mv /app/tmcprototype/DishLeafNode/coverage.xml /build/dishleafnode_coverage.xml; \
    fi;
.PHONY: all test
