#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc ska-tmc/ska-dish-master-mid/src/ska_dish_master_mid
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-cspmasterleafnode-mid/src/ska_tmc_cspmasterleafnode_mid
pylint --rcfile=.pylintrc ska-tmc/dishleafnode/src/ska-tmc-dishleafnode-mid
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-cspsubarrayleafnode-mid/src/ska_tmc_cspsubarrayleafnode_mid
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-sdpsubarrayleafnode-mid/src/ska_tmc_sdpsubarrayleafnode_mid
pylint --rcfile=.pylintrc ska-tmc/ska-tmc-sdpmasterleafnode-mid/src/ska_tmc_sdpmasterleafnode_mid
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
