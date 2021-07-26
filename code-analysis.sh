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
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-mccssubarrayleafnode/src/ska_tmc_mccssubarrayleafnode_low
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-mccsmasterleafnode-low/src/ska_tmc_mccsmasterleafnode_low
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-subarraynode-low/src/ska_tmc_subarraynode_low
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-centralnode-low/src/ska_tmc_centralnode_low

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
