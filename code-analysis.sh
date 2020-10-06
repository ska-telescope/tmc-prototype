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
pylint --rcfile=.pylintrc tmcprototype/mccssubarrayleafnode/src/mccssubarrayleafnode
pylint --rcfile=.pylintrc tmcprototype/mccsmasterleafnode/src/mccsmasterleafnode
pylint --rcfile=.pylintrc tmcprototype/subarraynode/src/subarraynode
pylint --rcfile=.pylintrc tmcprototype/centralnode/src/centralnode
pylint --rcfile=.pylintrc tmcprototype/subarraynode/src/subarraynodelow
pylint --rcfile=.pylintrc tmcprototype/centralnode/src/centralnodelow

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=.pylintrc tmcprototype/dishmaster/test
pylint --rcfile=.pylintrc tmcprototype/cspsubarrayleafnode/test
pylint --rcfile=.pylintrc tmcprototype/dishleafnode/test
pylint --rcfile=.pylintrc tmcprototype/cspmasterleafnode/test
pylint --rcfile=.pylintrc tmcprototype/sdpsubarrayleafnode/test
pylint --rcfile=.pylintrc tmcprototype/sdpmasterleafnode/test
pylint --rcfile=.pylintrc tmcprototype/mccssubarrayleafnode/test
pylint --rcfile=.pylintrc tmcprototype/mccsmasterleafnode/test
pylint --rcfile=.pylintrc tmcprototype/subarraynode/test
pylint --rcfile=.pylintrc tmcprototype/centralnode/test
pylint --rcfile=.pylintrc tmcprototype/subarraynodelow/test
pylint --rcfile=.pylintrc tmcprototype/centralnodelow/test
