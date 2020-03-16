#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc tmcprototype/dishmaster/src
pylint --rcfile=.pylintrc tmcprototype/cspsubarrayleafnode/src
pylint --rcfile=.pylintrc tmcprototype/dishleafnode/src
pylint --rcfile=.pylintrc tmcprototype/cspmasterleafnode/src
pylint --rcfile=.pylintrc tmcprototype/sdpsubarrayleafnode/src
pylint --rcfile=.pylintrc tmcprototype/sdpmasterleafnode/src
pylint --rcfile=.pylintrc tmcprototype/subarraynode/src
pylint --rcfile=.pylintrc tmcprototype/centralnode/src

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=.pylintrc tmcprototype/dishmaster/test
pylint --rcfile=.pylintrc tmcprototype/cspsubarrayleafnode/test
pylint --rcfile=.pylintrc tmcprototype/dishleafnode/test
pylint --rcfile=.pylintrc tmcprototype/cspmasterleafnode/test
pylint --rcfile=.pylintrc tmcprototype/sdpsubarrayleafnode/test
pylint --rcfile=.pylintrc tmcprototype/sdpmasterleafnode/test
pylint --rcfile=.pylintrc tmcprototype/subarraynode/test
pylint --rcfile=.pylintrc tmcprototype/centralnode/test
