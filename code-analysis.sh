#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc tmcprototype/DishMaster/DishMaster
pylint --rcfile=.pylintrc tmcprototype/DishLeafNode/DishLeafNode
pylint --rcfile=.pylintrc tmcprototype/CspMasterLeafNode/CspMasterLeafNode
pylint --rcfile=.pylintrc tmcprototype/SdpSubarrayLeafNode/SdpSubarrayLeafNode
pylint --rcfile=.pylintrc tmcprototype/SubarrayNode/SubarrayNode
pylint --rcfile=.pylintrc tmcprototype/CentralNode/CentralNode

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=.pylintrc tmcprototype/DishMaster/test
pylint --rcfile=.pylintrc tmcprototype/DishLeafNode/test
pylint --rcfile=.pylintrc tmcprototype/CspMasterLeafNode/test
pylint --rcfile=.pylintrc tmcprototype/SdpSubarrayLeafNode/test
pylint --rcfile=.pylintrc tmcprototype/SubarrayNode/test
pylint --rcfile=.pylintrc tmcprototype/CentralNode/test
