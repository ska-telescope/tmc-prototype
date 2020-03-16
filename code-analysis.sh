#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=.pylintrc tmcprototype/dishmaster/src
pylint --rcfile=.pylintrc tmcprototype/CspSubarrayLeafNode/CspSubarrayLeafNode
pylint --rcfile=.pylintrc tmcprototype/DishLeafNode/DishLeafNode
pylint --rcfile=.pylintrc tmcprototype/cspmasterleafnode/src
pylint --rcfile=.pylintrc tmcprototype/SdpSubarrayLeafNode/SdpSubarrayLeafNode
pylint --rcfile=.pylintrc tmcprototype/SdpMasterLeafNode/SdpMasterLeafNode
pylint --rcfile=.pylintrc tmcprototype/subarraynode/src
pylint --rcfile=.pylintrc tmcprototype/centralnode/src

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=.pylintrc tmcprototype/dishmaster/test
pylint --rcfile=.pylintrc tmcprototype/CspSubarrayLeafNode/test
pylint --rcfile=.pylintrc tmcprototype/DishLeafNode/test
pylint --rcfile=.pylintrc tmcprototype/cspmasterleafnode/test
pylint --rcfile=.pylintrc tmcprototype/SdpSubarrayLeafNode/test
pylint --rcfile=.pylintrc tmcprototype/SdpMasterLeafNode/test
pylint --rcfile=.pylintrc tmcprototype/subarraynode/test
pylint --rcfile=.pylintrc tmcprototype/centralnode/test
