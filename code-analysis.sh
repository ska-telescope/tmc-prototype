#!/usr/bin/env bash
echo "STATIC CODE ANALYSIS"
echo "===================="
echo

echo "MODULE ANALYSIS"
echo "---------------"
pylint --rcfile=rcfile tmcprototype/DishMaster/DishMaster
pylint --rcfile=rcfile tmcprototype/DishLeafNode/DishLeafNode
pylint --rcfile=rcfile tmcprototype/SubarrayNode/SubarrayNode
pylint --rcfile=rcfile tmcprototype/CentralNode/CentralNode

echo "TESTS ANALYSIS"
echo "--------------"
pylint --rcfile=rcfile tmcprototype/DishMaster/test
pylint --rcfile=rcfile tmcprototype/DishLeafNode/test
pylint --rcfile=rcfile tmcprototype/SubarrayNode/test
pylint --rcfile=rcfile tmcprototype/CentralNode/test
