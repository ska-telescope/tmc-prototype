#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc ska-tmc/dishmaster/src/dishmaster
pylint --rcfile=.pylintrc ska-tmc/cspsubarrayleafnode/src/cspsubarrayleafnode
pylint --rcfile=.pylintrc ska-tmc/dishleafnode/src/dishleafnode
pylint --rcfile=.pylintrc ska-tmc/cspmasterleafnode/src/cspmasterleafnode
pylint --rcfile=.pylintrc ska-tmc/sdpsubarrayleafnode/src/sdpsubarrayleafnode
pylint --rcfile=.pylintrc ska-tmc/sdpmasterleafnode/src/sdpmasterleafnode
pylint --rcfile=.pylintrc ska-tmc/mccssubarrayleafnode/src/mccssubarrayleafnode
pylint --rcfile=.pylintrc ska-tmc/mccsmasterleafnode/src/mccsmasterleafnode
pylint --rcfile=.pylintrc ska-tmc/subarraynodelow/src/subarraynodelow
pylint --rcfile=.pylintrc ska-tmc/centralnodelow/src/centralnodelow

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=.pylintrc ska-tmc/dishmaster/test
pylint --rcfile=.pylintrc ska-tmc/cspsubarrayleafnode/test
pylint --rcfile=.pylintrc ska-tmc/dishleafnode/test
pylint --rcfile=.pylintrc ska-tmc/cspmasterleafnode/test
pylint --rcfile=.pylintrc ska-tmc/sdpsubarrayleafnode/test
pylint --rcfile=.pylintrc ska-tmc/sdpmasterleafnode/test
pylint --rcfile=.pylintrc ska-tmc/mccssubarrayleafnode/test
pylint --rcfile=.pylintrc ska-tmc/mccsmasterleafnode/test
pylint --rcfile=.pylintrc ska-tmc/subarraynodelow/test
pylint --rcfile=.pylintrc ska-tmc/centralnodelow/test
