#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc src/ska_dish_master_mid/src/ska_dish_master_mid
pylint --rcfile=.pylintrc src/ska_tmc_cspmasterleafnode_mid/src/ska_tmc_cspmasterleafnode_mid
pylint --rcfile=.pylintrc src/ska_tmc_dishleafnode_mid/src/ska-tmc-dishleafnode-mid
pylint --rcfile=.pylintrc src/ska_tmc_cspsubarrayleafnode_mid/src/ska_tmc_cspsubarrayleafnode_mid
pylint --rcfile=.pylintrc src/ska_tmc_sdpsubarrayleafnode_mid/src/ska_tmc_sdpsubarrayleafnode_mid
pylint --rcfile=.pylintrc src/ska_tmc_sdpmasterleafnode_mid/src/ska_tmc_sdpmasterleafnode_mid
pylint --rcfile=.pylintrc src/ska_tmc_mccssubarrayleafnode_low/src/ska_tmc_mccssubarrayleafnode_low
pylint --rcfile=.pylintrc src/ska_tmc_mccsmasterleafnode_low/src/ska_tmc_mccsmasterleafnode_low
pylint --rcfile=.pylintrc src/ska_tmc_subarraynode_low/src/ska_tmc_subarraynode_low
pylint --rcfile=.pylintrc src/ska_tmc_centralnode_low/src/ska_tmc_centralnode_low

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
