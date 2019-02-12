all: test

# wait for the device to be available before beginning the test
# A temporary volume is mounted at /build when 'make test' is executing.
# The following steps copy across useful output to this volume which can
# then be extracted to form the CI summary for the test procedure.
test:
	retry -- tango_admin --check-device test/DishMaster/01
	cd app
	ls -l
	cd /app/tmc-prototype
#	cd /app/tmc-prototype/tmcprototype/DishMaster && python setup.py test | tee setup_py_test.stdout
#	cd /app/tmc-prototype/tmcprototype/DishMaster && ./code-analysis.sh | tee code_analysis.stdout
	if [ -d /build ]; then \
		mv /app/tmc-prototype/tmcprototype/DishMaster/setup_py_test.stdout /build; \
		mv /app/tmc-prototype/tmcprototype/DishMaster/code_analysis.stdout /build; \
		mv /app/tmc-prototype/tmcprototype/DishMaster/htmlcov /build; \
		mv /app/tmc-prototype/tmcprototype/DishMaster/coverage.xml /build; \
	fi;

.PHONY: all test
