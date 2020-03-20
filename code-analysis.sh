#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc tmcprototype/dishmaster/src/dishmaster
pylint --rcfile=.pylintrc tmcprototype/cspsubarrayleafnode/src/cspsubarrayleafnode
pylint --rcfile=.pylintrc tmcprototype/dishleafnode/src/dishleafnode
pylint --rcfile=.pylintrc tmcprototype/cspmasterleafnode/src/cspmasterleafnode
pylint --rcfile=.pylintrc tmcprototype/sdpsubarrayleafnode/src/sdpsubarrayleafnode
pylint --rcfile=.pylintrc tmcprototype/sdpmasterleafnode/src/sdpmasterleafnode
pylint --rcfile=.pylintrc tmcprototype/subarraynode/src/subarraynode
pylint --rcfile=.pylintrc tmcprototype/centralnode/src/centralnode

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
